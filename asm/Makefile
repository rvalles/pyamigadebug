as = vasmm68k_mot
asflags = -Fbin -phxass #-quiet
prepbb = ../helpers/bootblock_prepare.py
.PHONY: all
all: debug orange.o debugloop.o crc16.o crc16_xmodem.o crc32_nolut.o crc32c_nolut.o crc32.o crc32c.o memrecv.o memsend.o memsend_bne.o bootblock_dos.dd bootblock_debug.dd bootblock_optdebug.dd floppyxfer.o
debug:
	@echo "* assembling debug (cli/wb tool to just enter the debugger)..."
	$(as) -Fhunkexe -kick1hunks -phxass debug.S -o debug
orange.o: orange.S
	@echo "* assembling orange (set COLOR0 infinite loop)..."
	$(as) $(asflags) orange.S -o orange.o
debugloop.o: debugloop.S
	@echo "* assembling debugloop (SAD timeout workaround)..."
	$(as) $(asflags) debugloop.S -o debugloop.o
crc16.o: crc16.S
	@echo "* assembling crc16 (CRC-16/KERMIT)..."
	$(as) $(asflags) crc16.S -o crc16.o
crc16_xmodem.o: crc16_xmodem.S
	@echo "* assembling crc16_xmodem (CRC-16/XMODEM)..."
	$(as) $(asflags) crc16_xmodem.S -o crc16_xmodem.o
crc32.o: crc32.S
	@echo "* assembling crc32 (CRC-32/ISO-HDLC)..."
	$(as) $(asflags) crc32.S -o crc32.o
crc32c.o: crc32.S
	@echo "* assembling crc32c (CRC-32/ISCSI)..."
	$(as) $(asflags) crc32.S -Dcrc32c -o crc32c.o
crc32_nolut.o: crc32_nolut.S
	@echo "* assembling crc32 w/o lut (CRC-32/ISO-HDLC)..."
	$(as) $(asflags) crc32_nolut.S -o crc32_nolut.o
crc32c_nolut.o: crc32_nolut.S
	@echo "* assembling crc32c w/o lut (CRC-32/ISCSI)..."
	$(as) $(asflags) crc32_nolut.S -Dcrc32c -o crc32c_nolut.o
memsend.o: memsend.S
	@echo "* assembling memory send w/dbra loop..."
	$(as) $(asflags) memsend.S -o memsend.o
memsend_bne.o: memsend_bne.S
	@echo "* assembling memory send w/movl+bne loop..."
	$(as) $(asflags) memsend_bne.S -o memsend_bne.o
memrecv.o: memrecv.S
	@echo "* assembling memory receive..."
	$(as) $(asflags) memrecv.S -o memrecv.o
bootblock_dos.o: bootblock_dos.S
	@echo "* assembling bootblock that returns with d0=0 a0=dos_init..."
	$(as) $(asflags) bootblock_dos.S -o bootblock_dos.o
bootblock_dos.dd: bootblock_dos.o
	@echo "* preparing bootblock that returns with d0=0 a0=dos_init..."
	$(prepbb) bootblock_dos.o bootblock_dos.dd
bootblock_debug.o: bootblock_debug.S
	@echo "* assembling bootblock that calls debug..."
	$(as) $(asflags) bootblock_debug.S -o bootblock_debug.o
bootblock_debug.dd: bootblock_debug.o
	@echo "* preparing bootblock that calls debug..."
	$(prepbb) bootblock_debug.o bootblock_debug.dd
bootblock_optdebug.o: bootblock_optdebug.S
	@echo "* assembling bootblock that optionally calls debug..."
	$(as) $(asflags) bootblock_optdebug.S -o bootblock_optdebug.o
bootblock_optdebug.dd: bootblock_optdebug.o
	@echo "* preparing bootblock that optionally calls debug..."
	$(prepbb) bootblock_optdebug.o bootblock_optdebug.dd
floppyxfer.o: floppyxfer.S
	@echo "* assembling floppy xfer..."
	$(as) $(asflags) floppyxfer.S -o floppyxfer.o
clean:
	@echo "* Removing build artifacts..."
	rm -f debug orange.o debugloop.o crc16.o crc16_xmodem.o crc32_nolut.o crc32c_nolut.o crc32.o crc32c.o memrecv.o memsend.o memsend_bne.o bootblock_dos.o bootblock_dos.dd bootblock_debug.o bootblock_debug.dd bootblock_optdebug.o bootblock_optdebug.dd floppyxfer.o
