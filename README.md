# PicoFox – A Hackable 2m Fox Transmitter

**PicoFox** is an open source fox transmitter for the 2-meter amateur band, built around the
RP2040 microcontroller (the same chip used in the Raspberry Pi Pico). It’s designed to be simple,
functional, and easy to modify.

PicoFox works well as a standalone fox for portable or walking hunts, but it’s also a great platform
for experimentation. There's ample CPU, flash, and GPIO available if you want to add features like
sensors or interactivity. The transmitter can generate a frequency or phase modulated signal with up
to 2.5kHz (data) bandwidth.


## Key Features
- Transmits FM in the 144–148 MHz band (ITU Zone 1: 144–146 MHz).
- Configured by editing a text file — no software or terminal needed.
- Transmits any 5kHz 16-bit PCM WAV file.
- Automatic Morse code ID with configurable tone, speed, and spacing.
- RF output > 12dBm / 15mW.
- Charges over USB.
- Expansion header provides:
  - 12 GPIOs (including I2C, SPI, UART, ADC).
  - Regulated 3.3V and raw battery voltage.
  - Two additional SI5351 clock outputs


### Getting One

Fully assembled PicoFox units are available from [AI6YM.radio](https://ai6ym.radio/picofox). An
enclosure, battery, and antenna are included. I ship nearly anywhere in the world.

You can also build your own - both the hardware and software are open source for non-commercial use.
For commercial inquiries, contact [justin@ai6ym.radio](mailto:justin@ai6ym.radio).


## Configuration

To configure your PicoFox, connect it to any computer using a micro USB cable. It will appear as a
USB mass storage device (like a flash drive). Open `settings.txt` with a text editor and adjust the
configuration values as needed. Eject the drive, disconnect USB, and power cycle the PicoFox to
apply the new settings.

To reset to factory settings, delete `settings.txt`, eject the drive, disconnect USB, and power
cycle the PicoFox. A default settings file will be regenerated.


### Settings Overview

- `CALLSIGN`: Alphanumeric callsign (max 12 characters).
- `ITU_ZONE`: ITU zone where the transmitter operates (`1`, `2`, or `3`).
- `FREQ_MHZ`: Transmit frequency in MHz.
- `DUTY_CYCLE`: Transmit duty cycle percentage (`0–100`).
- `MORSE_WPM`: Morse ID speed in words per minute.
- `MORSE_FARNSWORTH_WPM`: Slower Farnsworth spacing speed (ignored if lower than `MORSE_WPM`).
- `MORSE_TONE`: Morse tone frequency (100–2000 Hz).
- `MORSE_TONE_VOL`: Morse tone volume percentage (`1–100`).

**Note:** Invalid or missing values may disable the transmitter or revert to safe defaults.


## Using the Transmitter

After configuring settings as described above. The transmitter will turn on following the
provided settings the next time it is turned on.

The transmitter may be powered by an external USB power supply or the internal battery. The internal
battery charges over USB but no indication is available to show battery charging.

**Note: The power switch must be ON to charge the battery over USB. The transmitter will run on USB
power with the switch OFF but the battery will NOT be charged.**

A full battery will last about five hours at 100% duty cycle, 


## Replacing the Audio File

To change the audio transmission, replace the `audio.wav` file in the device’s flash storage. The
audio must be sampled at **5kHz**, **mono** (one channel), and encoded as **signed 16-bit PCM WAV**.

Using **Audacity** (free software available for all major OSs):

1. Set "Project Rate (Hz)" to `5000`.
2. Import, record, or generate your audio.
3. Mix down to a single mono track.
4. Export as WAV using **Signed 16-bit PCM** encoding.
5. Name the file `audio.wav` and copy it to the device.
6. Eject the drive and disconnect USB.
7. Power cycle the PicoFox.

**Notes:**

- Improper format may prevent audio transmission or cause noise to be transmitted instead.
- The audio is transmitted, followed by the morse ID, and then the transmitter turns off if
  `DUTY_CYCLE < 100`. In this way the length of the audio determines the transmit cycle time and the
  frequency of morse code ID transmissions. **YOU ARE RESPONSIBLE FOR COMPLYING WITH LOCAL LAWS FOR
  TRANSMITTING YOUR CALLSIGN!**
- To restore the default audio, delete `audio.wav`, eject the drive, disconnect USB, and power cycle
  the PicoFox.


## Design Brief

An SI5351 clock generator, locked to a TCXO, provides the RF signal. Modulation is applied in
software by the RP2040. To achieve smooth FM output, modulation is handled on core 1 with
I<sup>2</sup>C running at 1 MHz. Register writes are minimized and no other devices are on
I<sup>2</sup>C0.

Core 0 manages flash operations. Most extensions or new features should run on core 0.

**Note:** Mounting the device as a USB mass storage device will interrupt clean modulation as both
cores are blocked during flash operations.

The SPI flash device is split into program memory and a FAT16 filesystem. The filesystem contains
a text file for user-supplied settings, an audio file for transmission, a second audio file
containing the generated morse code ID, and a hash file used to detect changes to the settings file.
Unexpected files are automatically deleted and missing files are re-created from defaults in the
firmware binary.

The design intentionally includes large amounts of free CPU cycles, RAM, and flash so that cool
things can be built on the PicoFox.


## Development Guide

### Build Environment Setup

- Install Arduino IDE >= 2.3.
- Install libraries - Adafruit SPIFlash, Adafruit TinyUSB, Etherkit Si5351.
- Install board package from [my fork of Arduino-Pico](https://github.com/ai6ym/arduino-pico). This
  will be merged upstream eventually but for now you'll need the changes in my fork.
- In `Tools -> Board` select the `Raspberry Pi RP2040/RP2350 Boards -> AI6YM PicoFox`.
- Connect your PicoFox and select the appropriate TTY / COM port.

On Linux it may be necessary to add udev rules for this device. The relevant rules from my system
are below. I have no idea how this works on other operating systems. Mac is probably similar,
Windows should not be used for software developement of any kind (or really anything).

```
# Make an RP2040 in BOOTSEL mode writable by all users, so you can `picotool`
# without `sudo`. 
SUBSYSTEM=="usb", ATTRS{idVendor}=="2e8a", ATTRS{idProduct}=="0003", MODE="0666"

# Symlink an RP2040 running MicroPython from /dev/pico.
#
# Then you can `mpr connect $(realpath /dev/pico)`.
SUBSYSTEM=="tty", ATTRS{idVendor}=="2e8a", ATTRS{idProduct}=="0005", SYMLINK+="pico"

# Adafruit TinyUSB stack.
SUBSYSTEM=="tty", ATTRS{idVendor}=="239a", ATTRS{idProduct}=="cafe", MODE="0666"
SUBSYSTEM=="usb", ATTRS{idVendor}=="239a", ATTRS{idProduct}=="cafe", MODE="0666"
```

### Compilation Settings

- `Flash Size`: `16MB (Sketch: 1MB, FS: 15MB)`
- `CPU Speed`: `TBD`
- `USB Stack`: `Adafruit TinyUSB`

If needed for some reason you could change the partition layout to give more space for the sketch.
Doing so would destroy all data but the code automatically formats the partition and writes
defaults.

All other settings are fine at default values.


### Recovering a Board

In general the UF2 upload process will work fine. Click the upload button, after compilation the IDE
will push the board into UF2 update mode, write the new binary, and then reset the board to normal
operation.

If that doesn't work try the following:
- Reset the board and try again. Just tap the `RESET` button on the board to reset the RP2040.
- Force the device into `BOOTSEL` mode. Hold the `BOOTSEL` button, tap the `RESET` button, and then
  release the `BOOTSEL` button.
- Force the device into `BOOTSEL` mode **AND** change `Tools -> Upload Method` to `PicoTool`.
- When all else fails grab a PicoProbe (or a Pico / Pico2 flashed with the PicoProbe binary),
  connect that to the debug header of the PicoFox, and change `Tools -> Upload Method` to
  `Picoprobe`.
- If all of the above fails, well, he's dead Jim.
