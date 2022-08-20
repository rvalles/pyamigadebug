as = vasmm68k_mot
asflags = -Fbin -phxass #-quiet
prepbb = ../helpers/bootblock_prepare.py
.PHONY: all
all: debug.o debug orange.o debugloop.o crc16.o crc16_xmodem.o crc32_nolut.o crc32c_nolut.o crc32.o crc32c.o memrecv.o memsend.o memsend_bne.o bootblock_dos.dd bootblock_debug.dd bootblock_optdebug.dd bootblock_strapexit.dd bootblock_warmdos.dd bootblock_noboot.dd floppyxfer.o
debug.o: debug.S
	@echo "* assembling debug (snippet to re-enter the debugger after a call)..."
	$(as) $(asflags) $< -o $@
debug: debug.S
	@echo "* assembling debug (cli/wb tool to just enter the debugger)..."
	$(as) -Fhunkexe -kick1hunks -phxass $< -o $@
orange.o: orange.S
	@echo "* assembling orange (set COLOR0 infinite loop)..."
	$(as) $(asflags) $< -o $@
debugloop.o: debugloop.S
	@echo "* assembling debugloop (SAD timeout workaround)..."
	$(as) $(asflags) $< -o $@
crc16.o: crc16.S
	@echo "* assembling crc16 (CRC-16/KERMIT)..."
	$(as) $(asflags) $< -o $@
crc16_xmodem.o: crc16_xmodem.S
	@echo "* assembling crc16_xmodem (CRC-16/XMODEM)..."
	$(as) $(asflags) $< -o $@
crc32.o: crc32.S
	@echo "* assembling crc32 (CRC-32/ISO-HDLC)..."
	$(as) $(asflags) $< -o $@
crc32c.o: crc32.S
	@echo "* assembling crc32c (CRC-32/ISCSI)..."
	$(as) $(asflags) $< -Dcrc32c -o $@
crc32_nolut.o: crc32_nolut.S
	@echo "* assembling crc32 w/o lut (CRC-32/ISO-HDLC)..."
	$(as) $(asflags) $< -o $@
crc32c_nolut.o: crc32_nolut.S
	@echo "* assembling crc32c w/o lut (CRC-32/ISCSI)..."
	$(as) $(asflags) $< -Dcrc32c -o $@
memsend.o: memsend.S
	@echo "* assembling memory send w/dbra loop..."
	$(as) $(asflags) $< -o $@
memsend_bne.o: memsend_bne.S
	@echo "* assembling memory send w/movl+bne loop..."
	$(as) $(asflags) $< -o $@
memrecv.o: memrecv.S
	@echo "* assembling memory receive..."
	$(as) $(asflags) $< -o $@
bootblock_dos.o: bootblock_dos.S
	@echo "* assembling bootblock that returns with d0=0 a0=dos_init..."
	$(as) $(asflags) $< -o $@
bootblock_dos.dd: bootblock_dos.o
	@echo "* preparing bootblock that returns with d0=0 a0=dos_init..."
	$(prepbb) $< $@
bootblock_debug.o: bootblock_debug.S
	@echo "* assembling bootblock that calls debug..."
	$(as) $(asflags) $< -o $@
bootblock_debug.dd: bootblock_debug.o
	@echo "* preparing bootblock that calls debug..."
	$(prepbb) $< $@
bootblock_optdebug.o: bootblock_optdebug.S
	@echo "* assembling bootblock that optionally calls debug..."
	$(as) $(asflags) $< -o $@
bootblock_optdebug.dd: bootblock_optdebug.o
	@echo "* preparing bootblock that optionally calls debug..."
	$(prepbb) $< $@
bootblock_strapexit.o: bootblock_strapexit.S
	@echo "* assembling bootblock that causes strap to actually return..."
	$(as) $(asflags) $< -o $@
bootblock_strapexit.dd: bootblock_strapexit.o
	@echo "* preparing bootblock that causes strap to actually return..."
	$(prepbb) $< $@
bootblock_warmdos.o: bootblock_warmdos.S
	@echo "* assembling bootblock that causes strap to actually return and start dos via WarmCapture()..."
	$(as) $(asflags) $< -o $@
bootblock_warmdos.dd: bootblock_warmdos.o
	@echo "* preparing bootblock that causes strap to actually return and start dos via WarmCapture()..."
	$(prepbb) $< $@
bootblock_noboot.dd: bootblock_noboot.S
	@echo "* assembling bootblock that AmigaOS won't recognize as bootable..."
	$(as) $(asflags) $< -o $@
floppyxfer.o: floppyxfer.S
	@echo "* assembling floppy xfer..."
	$(as) $(asflags) $< -o $@
clean:
	@echo "* Removing build artifacts..."
	rm -f debug *.o *.dd
