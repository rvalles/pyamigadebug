# Framework for abstracting Amiga debuggers.

This project provides abstration to control an Amiga remotely using a debugger.

The APIs are not yet stable.

I include an end-user ready GUI tool based on this, amigaXfer, as a preview.

# amigaXfer

This is a tool for data transfer between an Amiga and another computer using
the serial port. No agent required on Amiga's side, as it uses the kickstart
rom's debugger to take control of the Amiga.

There's multiple ways to get into this debugger. A simple one is through
Workbench's debug menu, present when wb is loaded using `loadwb -debug`.

Selecting the Debug, RomWack or SAD menu option in Workbench 1.x/2.x/3.x will
then enter the debugger and enable amigaXfer usage.

Alternatively, it is possible to bootstrap an Amiga for which no bootable disks
are available.

https://rvalles.net/bootstrapping-an-amiga-without-a-bootable-amiga-floppy.html

amigaXfer runs on multiple platforms. Windows binaries are provided in release
binary builds. Python 3.8+, PySerial and wxPython are required if running from
sources.

It is able to e.g. read/write/compare floppies, install bootblocks, send/receive
files and dump the kickstart rom.

Highlights:
* Uses the kickstart's serial debugger, and thus it does not require an agent.
* Supports RomWack (AmigaOS 1.x, 2.x) and SAD (AmigaOS 3.x) builtin debuggers.
* High speed transfers; 512kbps possible on basic 68000 @ 7MHz A500.
* Can be used to bootstrap an Amiga for which no bootable disks are available.
* Checksums (CRC32/ISO-HDLC) used throughout to ensure transfer integrity.
