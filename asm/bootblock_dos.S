_LVOFindResident equ -96
_LVOOldOpenLibrary equ -408
_LVOCloseLibrary equ -414
rt_Init equ 22
header:
    dc.b "DOS"
    dc.b 0 ;fs flags
    dc.l 0 ;checksum
    dc.l 880 ;root block
;bootblock env
;a1 trackdisk ioreq
;a6 execbase
;clobbering non-scratch regs is verified to be bad.
start:
    move.l a1,-(sp) ;ioreq, save as we'll clobber a1.
    lea.l expansionname(pc),a1
    jsr _LVOOldOpenLibrary(a6)
    tst.l d0
    beq.b .noexpansionlib
    movea.l d0,a1
    jsr _LVOCloseLibrary(a6)
.noexpansionlib
    lea.l dosname(pc),a1
    jsr _LVOFindResident(a6)
    tst.l d0
    bne.b .good ;if d0 != 0 that's good
    sub.l #1,d0 ;return bad
    rts
.good
    move.l d0,a0 ;a0 = romtag for dos.library
    move.l rt_Init(a0),a0
    move.l (sp)+,a1 ;compatibility with early ks. They need a1=ioreq.
    clr.l d0 ;return good
    rts
expansionname:
    dc.b "expansion.library",0
dosname:
    dc.b "dos.library",0
.banner
    dc.b "bootblock_dos",10
    dc.b "Standard-ish bootblock.",10
    dc.b "*** Bundled with amigaXfer.",10
    dc.b "(C) 2021 Roc Valles Domenech",10
    dc.b "https://www.rvalles.net",0
