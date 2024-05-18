Introduction
============


.. image:: https://readthedocs.org/projects/circuitpython-dmx-receiver/badge/?version=latest
    :target: https://circuitpython-dmx-receiver.readthedocs.io/
    :alt: Documentation Status



.. image:: https://img.shields.io/discord/327254708534116352.svg
    :target: https://adafru.it/discord
    :alt: Discord


.. image:: https://github.com/mydana/CircuitPython_DMX_Receiver/workflows/Build%20CI/badge.svg
    :target: https://github.com/mydana/CircuitPython_DMX_Receiver/actions
    :alt: Build Status


.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Code Style: Black


DMX512 lighting protocol receiver on the RP2040


Usage Example
=============

.. code-block:: Python

    "Receive DMX"

    import time
    import board
    from dmx_receiver import DmxReceiver

    DMX_PIN = board.D1

    dmx_receiver = DmxReceiver(pin=DMX_PIN, slot=0)

    for data in dmx_receiver:
        if data is not None:
            print(bytes(data))


Schematic
=========

Example::

>         ┌─────┐            ╔═════════════════╗
>    ╔════╡USB-C╞════╗       ║                 ║
>    ║    └─────┘    ║  ┌────╫(6) VCC          ║       ╔══════════════╗
>    ║            3V ╫──┘    ║               A ╫───────╫─< (3) Data + ║
>    ║               ║    NC─╫(2) TXD          ║  ┌────╫─< (2) Data - ║
>    ║               ║       ║               B ╫──┘ ┌──╫─< (1) Common ║
>    ║               ║   ┌───╫(4) RXD          ║    │  ╚══════════════╝
>    ║         RX/D1 ╫───┘   ║    __         Y ╫ NC │   XLR Connector
>    ║               ║    ┌──╫(1) RE           ║    │   Male
>    ║               ║    │  ║               Z ╫ NC │
>    ║               ║    ├──╫(4) DE           ║    │
>    ║           GND ╫────┤  ║          ISOGND ╫────┘
>    ║               ║    └──╫(5) GND          ║
>    ║               ║       ║                 ║
>    ╚═══════════════╝       ╚═════════════════╝
>     Microcontroller         RS485 Line Driver
>     Adafruit KB2040         Digilent PmodR485

    Significant DMX wiring requirements are necessarily out of scope
    in this document. Consult a qualified local expert.


REQUIREMENTS
============
**Hardware:**

* `Any RP2040 CircuitPython board. I used the Adafruit KB2040
  <https://www.adafruit.com/product/5302>`_ (Product ID: <5302>)

* An isolated RS485 line driver. I used a Digilent PmodRS485.

**Software and Dependencies:**

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_

* This library, dmx_transmitter, especially these files::

  * dmx_transmitter.mpy
  * payload_USITT_DMX512_A.mpy


Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_
or individual libraries can be installed using
`circup <https://github.com/adafruit/circup>`_.


Installing to a Connected CircuitPython Device with Circup
==========================================================

Make sure that you have ``circup`` installed in your Python environment.
Install it with the following command if necessary:

.. code-block:: shell

    pip3 install circup

With ``circup`` installed and your CircuitPython device connected use the
following command to install:

.. code-block:: shell

    circup install dmx_receiver

Or the following command to update an existing version:

.. code-block:: shell

    circup update


Documentation
=============
API documentation for this library can be found on `Read the Docs <https://circuitpython-dmx-receiver.readthedocs.io/>`_.

For information on building library documentation, please check out
`this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.


Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_
or individual libraries can be installed using
`circup <https://github.com/adafruit/circup>`_.


Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/mydana/CircuitPython_DMX_Receiver/blob/HEAD/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.
