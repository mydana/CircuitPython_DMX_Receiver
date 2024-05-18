# SPDX-FileCopyrightText: Copyright (c) 2024 Dana Runge
#
# SPDX-License-Identifier: Unlicense
"Receive DMX"

import board
from dmx_receiver import DmxReceiver

DMX_PIN = board.D1

dmx_receiver = DmxReceiver(pin=DMX_PIN, slot=0)

for data in dmx_receiver:
    if data is not None:
        print(bytes(data))
