# SPDX-FileCopyrightText: Copyright (c) 2024 Dana Runge
#
# SPDX-License-Identifier: MIT
"""
Receive DMX512 lighting data on a GPIO pin
------------------------------------------
"""

import array
import rp2pio
import adafruit_pioasm

__author__ = "Dana Runge"
__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/mydana/CircuitPython_DMX_Receiver"


class DmxProtocolError(Exception):
    """Raised when a broken DMX frame is detected"""


class DmxReceiver:
    """
    Receive 16 slots of DMX512 lighting data on a GPIO pin.

    Either explicitly request and retrieve data from the wire, or use this
    object as an iterator.

    Multiple objects may be used to receive more than 16 slots. Slots received
    from multiple objects need not be contiguous.
    """

    _PROGRAM = """
        .program DMX512RXc{0}
        .side_set 3
        fail:
            pull                     side 0     ; Run once & stall.
        break:
            set x, 20                side 0     ; BREAK: preload wait time
            wait 0 pin 0             side 0 [1] ; BREAK: wait for
        space:
            jmp pin break            side 0     ; BREAK: is NOT?
            jmp x-- space            side 0 [2] ; BREAK: wait time

            set x, {0}               side 0 [1] ; MARK AFTER BREAK: preload wait time. {{0}} in (2, 0)
            wait 1, pin 0            side 0     ; side! Waiting for MARK AFTER BREAK
        mark_after_break:
            jmp pin ok               side 0     ; MARK AFTER BREAK: IS marking?
            jmp break                side 0     ; MARK AFTER BREAK: is NOT marking!
        ok:
            jmp x-- mark_after_break side 0     ; MARK AFTER BREAK: wait time

            wait 0 pin 0             side 0     ; NULL START: start bit
            set x, 15                side 0     ; NULL START: preload wait time
        null_start_check:
            jmp pin break            side 0     ; NULL START: is NOT!
            jmp x-- null_start_check side 0     ; NULL START: wait time
            nop                      side 0 [1] ; NULL START: wait 4 stop
            jmp pin null_stop_2      side 0 [2] ; NULL START: stop bit 1?
            jmp break                side 0     ; NULL START: IS NOT!
        null_stop_2:
            jmp pin data_start       side 0     ; NULL START: stop bit 2?
            jmp break                side 0     ; NULL START: IS NOT!
        data_start:
            mov isr, null            side 0     ; DATA: reject data
        .wrap_target
            wait 0 pin 0             side 0     ; DATA: start bit
            set x, 7                 side 0     ; DATA: preload bit count
            jmp pin fail             side 0     ; DATA: verify start bit
            nop                      side 0     ; DATA: wait for lsb
        bitloop:
            in pins, 1               side 0     ; DATA: sample the data
            jmp x-- bitloop          side 0 [2] ; DATA: more data?
            jmp pin data_stop_2      side 0 [3] ; DATA: stop bit 1?
            jmp fail                 side 0     ; DATA: is NOT!
        data_stop_2:
            jmp pin good_data        side 0     ; DATA: stop bit 2?
            jmp fail                 side 0     ; DATA: is NOT!
        good_data:
            jmp y-- data_start       side 0     ; Ctrl: reject unwanted DMX slots
            set y, 0                 side 0     ; Ctrl: never skip again
        .wrap
    """

    def __init__(self, pin, dmx_basis=False, slot=None):
        """
        Configure up the RP2040 state machine::

        :param ~microcontroller.pin pin: The pin to retrieve data from.
        :param boolean dmx_basis: If True start slot numbers at 1 not 0.
        :param int slot: The first DMX slot of 16 to listen for.
        """
        self.pin = pin
        self._basis = 1 if dmx_basis else 0
        self._slot = 0 if slot is None else int(slot)
        self._sm_slot = None
        self.state_machine = None

    def __iter__(self):
        self.bind()
        return self

    def __next__(self):
        try:
            data = self.recvfrom()
        except DmxProtocolError:
            self.bind()
            return None
        self.bind()
        return data

    @property
    def slot(self):
        """
        The slot requested
        """
        return self._slot + self._basis

    @slot.setter
    def slot(self, value):
        value = int(value) - self._basis
        if value < 0:
            if self._basis:
                raise ValueError("slot shall be 1 or greater")
            raise ValueError("slot shall be 0 or greater")
        if value >= (512 - 16):
            raise ValueError("Slot number too large.")
        if value % 2:
            raise ValueError(
                "Due to technical limitations, "
                f"slot must be an {'odd' if self._basis else 'even'} number."
            )
        self._slot = value

    def bind(self, slot=None):
        """
        Set up the RP2040 state machine to retrieve data.

        :param int slot: The first DMX slot of 16 to listen for.
        :rtype: None
        """
        if slot is not None:
            self._slot = slot
        if self._sm_slot != self._slot:
            if self.state_machine:
                self.state_machine.deinit()
            init = adafruit_pioasm.assemble(
                """
                set y, {1}    ; lsn - least significant nybble
                in y, 4
                set y, {0}    ; msn - most significant nybble
                in y, 4
                in null, 23   ; bit count cannot be >= 32 to stop auto pull.
                mov y, isr    ; bit count.
                mov isr, null ; clear isr, even though we don't need to.

                jmp 1         ; Ctrl: start program.
            """.format(
                    *divmod((self._slot) // 2, 16)
                )
            )
            self.state_machine = rp2pio.StateMachine(
                self.program.assembled,
                **self.program.pio_kwargs,
                init=init,
                frequency=1_000_000,
                first_in_pin=self.pin,
                jmp_pin=self.pin,
                exclusive_pin_use=False,
                auto_push=True,
                push_threshold=32,
                first_sideset_pin=None,  # TODO
                initial_sideset_pin_state=31,  # TODO
            )
            self._sm_slot = self._slot
        else:
            self.state_machine.clear_rxfifo()
            self.state_machine.clear_txstall()
            self.state_machine.restart()

    def recvfrom(self):
        """
        Receive data from the wire if available.

        :return: 16 slots of DMX data
        :rtype: bytes or None
        :raises DmxProtocolError: a broken DMX frame is detected
        """
        rx_buff = memoryview(array.array("L", [2**32 - 1] * 4))
        if self.state_machine.txstall:
            raise DmxProtocolError("A broken DMX frame was detected.")
        if not self.state_machine.in_waiting >= len(rx_buff):
            return None
        self.state_machine.stop()
        self.state_machine.readinto(rx_buff)
        return bytes(rx_buff.cast("B"))


# TODO: This line allows for supporting a very old version of the
# TODO: DMX512 standard. Factor it out when factoring out pioasm.
# pylint: disable=protected-access
DmxReceiver.program = adafruit_pioasm.Program(DmxReceiver._PROGRAM.format(2))  #
