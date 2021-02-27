# Framework for abstracting Amiga debuggers.

APIs are not yet stable.

I include a tool based on this, amigaXfer, as a preview.

This is a tool for data transfer between an Amiga and another computer using
the serial port. No agent required on Amiga's side.

It is possible to bootstrap an Amiga for which no bootable disks are available.

https://rvalles.net/bootstrapping-an-amiga-without-a-bootable-amiga-floppy.html

Source code (python and m68k assembly) is available under MIT license, and runs
on multiple platforms, requiring Python 3.8+, pyserial and wxpython.

Highlights:
* Uses the kickstart's serial debugger, and thus it does not require an agent.
* Supports RomWack (AmigaOS 1.x, 2.x) and SAD (AmigaOS 3.x) builtin debuggers.
* High speed transfers; 512kbps possible on basic 68000 @7MHz A500.
* Can be used to bootstrap an Amiga for which no bootable disks are available.
* Checksums (CRC32/ISO-HDLC) used throughout to ensure transfer integrity.
