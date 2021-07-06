_LVODoIO equ -456
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
    move.l a1,a3 ;preserve ioreq for older kickstarts
    move.w #TD_MOTOR,io_Command(a1)
    clr.l io_Length(a1)
    jsr _LVODoIO(a6) ;turn boot drive motor off
    move.l a3,a1 ;restore ioreq for older kickstarts
    lea.l .reusablerts,a0
    clr.l d0 ;return good
.reusablerts
    rts
.banner
    dc.b "bootblock_strapexit", 10
    dc.b "Makes strap exit, allowing exec InitCode() to continue.",10
    dc.b "*** Bundled with amigaXfer.",10
    dc.b "(C) 2021 Roc Valles Domenech",10
    dc.b "https://www.rvalles.net",0
