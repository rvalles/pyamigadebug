_LVOFindResident equ -96
_LVODebug equ -114
_LVOAllocMem = -198
_LVOOldOpenLibrary equ -408
_LVOCloseLibrary equ -414
_LVODoIO equ -456
_LVOAddIntServer equ -168
_LVOLoadView equ -222
rt_Init equ 22
io_Command equ $1c
io_Length equ $24
TD_MOTOR equ 9
MEMF_PUBLIC equ 1
NT_INTERRUPT equ 2
ln_Type equ 8
ln_Pri equ 9
ln_Name equ 10
is_Data equ 14
is_Code equ 18
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
    move.w #$0FD8,$dff180 ;color to orange. It should never be seen.
    move.l a1,-(sp) ;ioreq backup, as there it should survive calls.
    lea.l graphicsname,a1
    jsr _LVOOldOpenLibrary(a6)
    movea.l d0,a6
    movea.l #0,a1
    jsr _LVOLoadView(a6) ;as kick wb floppy prompt leaves a view set.
    movea.l a6,a1
    movea.l $4,a6
    jsr _LVOCloseLibrary(a6)
    move.l #$bfd100,a0
    btst #6,$bfe001
    beq .normalboot ;left mouse button always boot normally
    bset #1,$bfe001 ;filter off
    btst #14,$dff018 ;SERDATR RBF
    bne debug ;if serial input, debug
    btst #2,$dff016 ;POTINP DATLY
    beq debug ;right mouse always debug
    move.l #22, d0
    move.l #MEMF_PUBLIC, d1
    jsr _LVOAllocMem(a6) ;get ram for Interrupt structure.
    movea.l d0, a1
    move.b #NT_INTERRUPT, ln_Type(a1)
    move.b #0, ln_Pri(a1)
    move.l #0, ln_Name(a1)
    move.l #0, is_Data(a1)
    lea.l _LVODebug(a6), a0
    move.l a0, is_Code(a1)
    move.l #15, d0 ;Level7 (NMI)
    jsr _LVOAddIntServer(a6)
.normalboot
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
    bne good ;if d0 != 0 that's good
    move.w #$0F0F,$dff180 ;color for this odd situation
    sub.l #1,d0 ;return bad
    rts
expansionname:
    dc.b "expansion.library",0
dosname:
    dc.b "dos.library",0
graphicsname:
    dc.b "graphics.library",0
    even
good:
    move.l d0,a0 ;a0 = romtag for dos.library
    move.l rt_Init(a0),a0
    clr.l d0 ;return good
    move.l (sp)+,a1 ;compatibility with early ks. They need a1=ioreq.
    move.w #$024D,$dff180 ;set color to show this custom bootblock is booting
    rts
debug:
    move.l (sp)+,a1 ;restore ioreq as we need to do i/o
    move.w #TD_MOTOR,io_Command(a1)
    clr.l io_Length(a1)
    jsr _LVODoIO(a6) ;turn boot drive motor off
    move.w #$00F0,$dff180 ;green screen before calling debug
    jsr _LVODebug(a6)
    move.w #$0F00,$dff180 ;red screen when returning from debug
    rts
.banner
    dc.b "bootblock_optdebug", 10
    dc.b "Exec->Debug() on serial input or right mouse button held.",10
    dc.b "Hold left mouse button to always boot normally.",10
    dc.b "Disables audio filter and installs debug() as NMI server unless LMB held.",10
    dc.b "*** Bundled with amigaXfer.",10
    dc.b "(C) 2021 Roc Valles Domenech",10
    dc.b "https://www.rvalles.net",0
