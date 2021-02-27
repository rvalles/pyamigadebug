;Memory to serial transfer.
;Starts sending when there's an incoming character on serial.
;a0 addr, d0 size, d1w SERPER, d1hw original SERPER.
memsend:
    move.l #$DFF018,a1 ;SERDATR
    btst #12,(a1) ;SERDATR TSRE, as we change serper
    beq memsend
    move.w d1,26(a1) ;SERPER
.waitforserialin
    btst #14,(a1) ;SERDATR RBF
    beq .waitforserialin
    move.w #$0800,132(a1) ;INTREQ RBF clear
    cmp.l #0,d0
    beq .done
    move.w #$01FF,d1
.loop
    btst #13,(a1) ;SERDATR TBE
    beq .loop
    move.b (a0)+,d1
    move.w d1,24(a1) ;SERDAT
    sub.l #1,d0
    bne .loop
.done
    btst #12,(a1) ;SERDATR TSRE, as we will change serper.
    beq .done
    swap d1
    move.w d1,26(a1) ;SERPER
.waitforserialend
    btst #14,(a1) ;SERDATR RBF
    beq .waitforserialend
    move.w #$0800,132(a1) ;INTREQ RBF clear
    rts
