import io
import os
import re
import time
import board
import storage
import usb_hid
import digitalio

from adafruit_hid.consumer_control_code import ConsumerControlCode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.mouse import Mouse

# Switch 2 test profile: boot.py exposes only the keyboard HID device.
# Do not instantiate Mouse or ConsumerControl; those interfaces are disabled.
cc = None
kb = Keyboard(usb_hid.devices)
ms = None
bt = digitalio.DigitalInOut(board.GP25)
bt.direction = digitalio.Direction.INPUT
bt.pull = digitalio.Pull.UP

led = digitalio.DigitalInOut(board.GP12)
led.direction = digitalio.Direction.OUTPUT
led.value = True

looping = False
loop_pos = 0

def execute_command(function, command):
    if function == "DELAY":
        if command.isdigit():
            time.sleep(float(command))
    elif function == "PRESS":
        command = command.split(" + ")
        for c in range(0, len(command), 1):
            command[c] = command[c].upper()
        if len(command) <= 6:
            keys = [0] * len(command)
            for idx in range(0, len(command), 1):
                keys[idx] = getattr(Keycode, command[idx])
            # Keep key-down and key-up in separate reports for long enough
            # that slower USB hosts (including the Switch 2) can poll both.
            # kb.send() releases immediately and can make short taps such as
            # ENTER disappear on some hosts.
            kb.press(*keys)
            time.sleep(0.05)
            kb.release_all()
            time.sleep(0.05)
    elif function == "WRITE":
        layout.write(command)
    elif function == "HOLD":
        command = command.split(" + ")
        for c in range(0, len(command), 1):
            command[c] = command[c].upper()
        if len(command) <= 6:
            keys = [0] * len(command)
            for idx in range(0, len(command), 1):
                keys[idx] = getattr(Keycode, command[idx])
            kb.press(*keys)
    elif function == "RELEASE":
        kb.release_all()
    elif function == "MOVE":
        # Mouse HID is intentionally unavailable in the keyboard-only profile.
        if ms is not None:
            command = command.split(", ")
            pos = [0] * 2
            for i in range(0, len(command), 1):
                pos[i] = int(command[i])
            ms.move(x=pos[0], y=-1*pos[1], wheel=0)
    elif function == "SCROLL":
        if ms is not None:
            ms.move(x=0, y=0, wheel=int(command))
    elif function == "CLICK":
        if ms is not None:
            if command == "left":
                ms.click(Mouse.LEFT_BUTTON)
            elif command == "middle":
                ms.click(Mouse.MIDDLE_BUTTON)
            elif command == "right":
                ms.click(Mouse.RIGHT_BUTTON)
    elif function == "VOLUME":
        # Consumer/media-control HID is intentionally unavailable in this profile.
        if cc is not None:
            if command.isdigit():
                for vc in range(0, abs(int(command)), 1):
                    if int(command) > 0:
                        cc.send(ConsumerControlCode.VOLUME_INCREMENT)
                    elif int(command) < 0:
                        cc.send(ConsumerControlCode.VOLUME_DECREMENT)
            elif command == "mute":
                cc.send(ConsumerControlCode.MUTE)

def get_substr(string, start, end):
    command = ""
    for idx in range(start+1, end):
        command += string[idx]
    return command

try:
    file = io.open("/layout.txt", "r")
    line = file.readline()
    command = get_substr(line, line.find("("), line.rfind(")"))
    if command == "US":
        from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
        layout = KeyboardLayoutUS(kb)
    elif command == "CRO":
        from keyboard_layouts.keyboard_layout_win_cr import KeyboardLayout
        layout = KeyboardLayout(kb)
    elif command == "UK":
        from keyboard_layouts.keyboard_layout_win_uk import KeyboardLayout
        layout = KeyboardLayout(kb)
    elif command == "FR":
        from keyboard_layouts.keyboard_layout_win_fr import KeyboardLayout
        layout = KeyboardLayout(kb)
    elif command == "CZ":
        from keyboard_layouts.keyboard_layout_win_cz import KeyboardLayout
        layout = KeyboardLayout(kb)
    elif command == "BR":
        from keyboard_layouts.keyboard_layout_win_br import KeyboardLayout
        layout = KeyboardLayout(kb)
    elif command == "DE":
        from keyboard_layouts.keyboard_layout_win_de import KeyboardLayout
        layout = KeyboardLayout(kb)
    elif command == "ES":
        from keyboard_layouts.keyboard_layout_win_es import KeyboardLayout
        layout = KeyboardLayout(kb)
    elif command == "HU":
        from keyboard_layouts.keyboard_layout_win_hu import KeyboardLayout
        layout = KeyboardLayout(kb)
    elif command == "IT":
        from keyboard_layouts.keyboard_layout_win_it import KeyboardLayout
        layout = KeyboardLayout(kb)
    elif command == "PO":
        from keyboard_layouts.keyboard_layout_win_po import KeyboardLayout
        layout = KeyboardLayout(kb)
    elif command == "SW":
        from keyboard_layouts.keyboard_layout_win_sw import KeyboardLayout
        layout = KeyboardLayout(kb)
    elif command == "TR":
        from keyboard_layouts.keyboard_layout_win_tr import KeyboardLayout
        layout = KeyboardLayout(kb)
    elif command == "BE":
        from keyboard_layouts.keyboard_layout_win_bene import KeyboardLayout
        layout = KeyboardLayout(kb)
    elif command == "SG":
        from keyboard_layouts.keyboard_layout_win_sg import KeyboardLayout
        layout = KeyboardLayout(kb)
    file = io.open("/pico_usb.txt", "r")
    line = file.readline()
    while line != "":
        function = line.split("(",1)[0].upper()
        command = get_substr(line, line.find("("), line.rfind(")"))
        if looping == False:
            loop_pos += len(line)
        if function == "LOOP":
            looping = True
        execute_command(function, command)
        line = file.readline()
    file.close()
    file = io.open("/pico_usb.txt", "r")
    while looping == True:
        file.seek(loop_pos)
        line = file.readline()
        while line != "":
            function = line.split("(",1)[0].upper()
            command = get_substr(line, line.find("("), line.rfind(")"))
            execute_command(function, command)
            line = file.readline()
    file.close()

except OSError as e:
    print(e)
kb.release_all()
