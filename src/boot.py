#   Copyright 2024 PicoUSB
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
"""PicoUSB boot.py with a keyboard-only USB profile for Switch 2 testing."""

import time
import board
import storage
import digitalio
import microcontroller
import usb_cdc
import usb_hid

# A CDC serial console is unnecessary for PicoUSB payload execution and can
# make the device appear as a composite device. Disable it before USB starts.
usb_cdc.disable()

mode = digitalio.DigitalInOut(board.GP25)
mode.direction = digitalio.Direction.INPUT
mode.pull = digitalio.Pull.UP

storage.remount("/", readonly=False)
m = storage.getmount("/")
m.label = "PicoUSB"
storage.remount("/", readonly=True)
storage.enable_usb_drive()
time.sleep(0.1)  # wait a bit so the button gets pulled up

if mode.value:
    # Normal run: expose only a standard boot-keyboard interface.
    storage.disable_usb_drive()
    usb_hid.enable((usb_hid.Device.KEYBOARD,), boot_device=1)
else:
    time.sleep(0.1)  # check again after 100 ms to avoid a spurious button read
    if mode.value:
        storage.disable_usb_drive()
        usb_hid.enable((usb_hid.Device.KEYBOARD,), boot_device=1)
    else:
        # Mode button held: retain the original file-edit/safe-mode workflow.
        # No HID keyboard is needed while mounting the drive for editing.
        storage.enable_usb_drive()
        usb_hid.disable()
        microcontroller.on_next_reset(microcontroller.RunMode.SAFE_MODE)
        microcontroller.reset()

# In case you accidentally disable the USB drive without a failsafe, original
# PicoUSB recovery approach: from the REPL call microcontroller.on_next_reset
# (microcontroller.RunMode.SAFE_MODE) and microcontroller.reset().
