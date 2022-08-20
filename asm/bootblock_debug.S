COLOR00 equ $dff180
_LVODebug equ -114
_LVODoIO equ -456
_LVOOldOpenLibrary equ -408
_LVOCloseLibrary equ -414
_LVOLoadView equ -222
io_Command equ $1c
io_Length equ $24
TD_MOTOR equ 9
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
    move.l a1,a3
    lea.l .graphicsname,a1
    jsr _LVOOldOpenLibrary(a6)
    movea.l d0,a6
    movea.l #0,a1
    jsr _LVOLoadView(a6) ;as kick wb floppy prompt leaves a view set.
    movea.l a6,a1
    movea.l $4,a6
    jsr _LVOCloseLibrary(a6)
    move.l a3,a1
    move.w #TD_MOTOR,io_Command(a1)
    clr.l io_Length(a1)
    jsr _LVODoIO(a6) ;turn boot drive motor off
    move.w #$0AFA,COLOR00 ;green screen before calling debug.
.debugloop
    jsr _LVODebug(a6)
    move.w #$0FAA,COLOR00 ;red screen when returning from debug
    bra .debugloop
.graphicsname
    dc.b "graphics.library",0
.banner
    dc.b "bootblock_debug", 10
    dc.b "Calls Exec->Debug() in a loop.",10
    dc.b "*** Bundled with amigaXfer.",10
    dc.b "(C) 2022 Roc Valles Domenech",10
    dc.b "https://www.rvalles.net",0
