FX_NOP equ $00
FX_EXIT equ $ff
FX_SETBUFFER equ $01
FX_SETLENGTH equ $02
FX_SETIOREQ equ $03
FX_SETTRACK equ $04
FX_SETUSR equ $05
FX_SENDBUFFER equ $20
FX_RECVBUFFER equ $21
FX_CALLUSR equ $25
FX_TRACKREAD equ $30
FX_TRACKFORMAT equ $31
FX_TRACKSEEK equ $32
FX_MOTOROFF equ $40
CMD_READ equ 2
CMD_CLEAR equ 5
TD_SEEK equ 10
TD_MOTOR equ 9
TD_FORMAT equ 11
io_Command equ $1c
io_Flags equ $1e
io_Error equ $1f
io_Length equ $24
io_Data equ $28
io_Offset equ $2c
_LVODoIO equ -456
TRACKSIZE equ 5632
;params: d0w SERPER, d0hw original SERPER.
floppyxfer:
    movem.l a2-a6/d2-d6,-(sp)
    move.l $4,a6 ;execbase
    move.l #$DFF018,a2 ;SERDATR
.busyserial ;wait for transfer idle before changing SERPER
    btst #12,(a2) ;SERDATR TSRE, as we change serper
    beq .busyserial
    move.w d0,26(a2) ;SERPER
    swap d0
    move.w d0,-(sp)
    bsr recvbyte
    bra mainloop
sendbyte: ;d0 char to send, a2 SERDATR
    btst #13,(a2) ;SERDATR TBE
    beq sendbyte
    move.w #$0100,d1
    move.b d0,d1
    move.w d1,24(a2) ;SERDAT
    rts
sendlong: ;d0 long to send, a2 SERDATR
    move.l d2,-(sp)
    move.w #3,d2
.sendlongloop
    rol.l #8,d0
    bsr sendbyte
    dbra d2,.sendlongloop
    move.l (sp)+,d2
    rts
recvbyte:  ;a2 SERDATR, returns read char at d0b
    move.w (a2),d0 ;SERDATR RBF
    btst #14,d0 ;SERDATR RBF
    beq recvbyte
    move.w #$0800,132(a2) ;INTREQ RBF clear
    rts
recvlong: ;a2 SERDATR, returns read long at d0
    movem.l d2,-(sp)
    move.b #$48,d0 ;'H' high word, high byte
    bsr sendbyte
    bsr recvbyte
    move.b d0,d2
    lsl.w #8,d2
    move.b #$68,d0 ;'h' high word, low byte
    bsr sendbyte
    bsr recvbyte
    move.b d0,d2
    swap d2
    move.b #$4c,d0 ;'L' low word, high byte
    bsr sendbyte
    bsr recvbyte
    move.b d0,d2
    lsl.w #8,d2
    move.b #$6c,d0 ;'l' low word, low byte
    bsr sendbyte
    bsr recvbyte
    move.b d0,d2
    move.l d2,d0
    movem.l (sp)+,d2
    rts
;a6 execbase
;a5 usr(), user subroutine addr
;a4 ioreq addr
;a3 buffer addr
;a2 SERDATR
;d6 buffer size
;d5 track
mainloop:
    move.b #$3f,d0 ;'?'
    bsr sendbyte
    bsr recvbyte
    cmp.b #FX_NOP,d0 ;nop
    beq mainloop
    cmp.b #FX_EXIT,d0
    beq cmdexit
    cmp.b #FX_SETBUFFER,d0
    beq cmdsetbuffer
    cmp.b #FX_SETLENGTH,d0
    beq cmdsetlength
    cmp.b #FX_SETIOREQ,d0
    beq cmdsetioreq
    cmp.b #FX_SETTRACK,d0
    beq cmdsettrack
    cmp.b #FX_SETUSR,d0
    beq cmdsetusr
    cmp.b #FX_CALLUSR,d0
    beq cmdcallusr
    cmp.b #FX_SENDBUFFER,d0
    beq cmdsendbuffer
    cmp.b #FX_RECVBUFFER,d0
    beq cmdrecvbuffer
    cmp.b #FX_TRACKREAD,d0
    beq cmdtrackread
    cmp.b #FX_TRACKFORMAT,d0
    beq cmdtrackformat
    cmp.b #FX_TRACKSEEK,d0
    beq cmdtrackseek
    cmp.b #FX_MOTOROFF,d0
    beq cmdmotoroff
    move.b #$21,d0 ;'!'
    bsr sendbyte
    bra mainloop
cmdexit:
    btst #12,(a2) ;SERDATR TSRE, as we will change serper.
    beq cmdexit
    move.w (sp)+,d0
    move.w d0,26(a2) ;SERPER restore
.waitforserialend
    btst #14,(a2) ;SERDATR RBF
    beq .waitforserialend
    move.w #$0800,132(a2) ;INTREQ RBF clear
    movem.l (sp)+,a2-a6/d2-d6
    rts
cmdsetbuffer:
    bsr recvlong
    move.l d0,a3
    bra mainloop
cmdsetlength:
    bsr recvlong
    move.l d0,d6
    bra mainloop
cmdsetioreq:
    bsr recvlong
    move.l d0,a4
    bra mainloop
cmdsettrack:
    bsr recvlong
    move.l d0,d5
    bra mainloop
cmdsetusr:
    bsr recvlong
    move.l d0,a5
    bra mainloop
cmdcallusr: ;meant for crc32() and such
    movem.l a2-a6/d2-d6,-(sp)
    move.l a3,a0 ;buffer address at a0
    move.l d6,d0 ;buffer size at d0
    jsr (a5)
    movem.l (sp)+,a2-a6/d2-d6
    bsr sendlong
    bra mainloop
cmdsendbuffer:
    move.l a3,a0 ;buffer addr
    move.l d6,d0 ;buffer size
    cmp.l #0,d0
    beq .done
    move.w #$01FF,d1
    sub.l #1,d0
    bra .loop
.oloop
    swap d0
.loop
    btst #13,(a2) ;SERDATR TBE
    beq .loop
    move.b (a0)+,d1
    move.w d1,24(a2) ;SERDAT
    dbra d0,.loop
    swap d0
    dbra d0,.oloop
.done
    bra mainloop
cmdrecvbuffer:
    move.l a3,a0 ;buffer addr
    move.l d6,d0 ;buffer size
    move.w #$0800,132(a2) ;INTREQ RBF clear
    move.w #$0153,d1 ;'S'
.waitforserialready
    btst #13,(a2) ;SERDATR TBE
    beq .waitforserialready
    move.w d1,24(a2) ;SERDAT
    cmp.l #0,d0
    beq .done
.loop
    move.w (a2),d1 ;SERDATR RBF
    btst #14,d1 ;SERDATR RBF
    beq .loop
    move.w #$0800,132(a2) ;INTREQ RBF clear 
    ;move.w #$0800,$dff09c ;INTREQ RBF clear
    move.b d1,(a0)+
    sub.l #1,d0
    bne .loop
.done
    bra mainloop
trackclear:
    move.w #CMD_CLEAR,io_Command(a1)
    move.b #0,io_Flags(a1)
    jsr _LVODoIO(a6)
    rts
cmdtrackread:
    move.l a4,a1 ;ioreq
    jsr trackclear
    move.w #CMD_READ,io_Command(a1)
    move.b #0,io_Flags(a1)
    move.l a3,io_Data(a1)
    move.l d6,io_Length(a1)
    move.l d5,d0
    mulu.w #TRACKSIZE,d0
    move.l d0,io_Offset(a1)
    bra doio
cmdtrackformat:
    move.l a4,a1 ;ioreq
    jsr trackclear
    move.w #TD_FORMAT,io_Command(a1)
    move.b #0,io_Flags(a1)
    move.l a3,io_Data(a1)
    move.l d6,io_Length(a1)
    move.l d5,d0
    mulu.w #TRACKSIZE,d0
    move.l d0,io_Offset(a1)
    bra doio
cmdtrackseek:
    move.l a4,a1 ;ioreq
    move.w #TD_SEEK,io_Command(a1)
    move.b #0,io_Flags(a1)
    move.l d5,d0
    mulu.w #TRACKSIZE,d0
    move.l d0,io_Offset(a1)
    bra doio
cmdmotoroff:
    move.l a4,a1 ;ioreq
    move.w #TD_MOTOR,io_Command(a1)
    move.l #0,io_Length(a1)
    move.l d5,io_Offset(a1)
doio:
    jsr _LVODoIO(a6)
    bsr sendbyte ;ioerr
    bra mainloop
