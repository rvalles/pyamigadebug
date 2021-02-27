;Serial to memory transfer.
;Waits for incoming character, sends S, then starts receiving the data.
;a0 addr, d0 size, d1w SERPER, d1hw original SERPER.
memrecv:
    move.l #$DFF018,a1 ;SERDATR
    btst #12,(a1) ;SERDATR TSRE, as we change serper
    beq memrecv
    move.w d1,26(a1) ;SERPER
.waitforserialin
    btst #14,(a1) ;SERDATR RBF
    beq .waitforserialin
    move.w #$0800,132(a1) ;INTREQ RBF clear
    move.w #$0153,24(a1) ;'S', SERDAT
.waitforcharsent
    btst #13,(a1) ;SERDATR TBE
    beq .waitforcharsent
    cmp.l #0,d0
    beq .done
.loop
    move.w (a1),d1 ;SERDATR RBF
    btst #14,d1 ;SERDATR RBF
    beq .loop
    move.w #$0800,132(a1) ;INTREQ RBF clear 
    ;move.w #$0800,$dff09c ;INTREQ RBF clear
    move.b d1,(a0)+
    sub.l #1,d0
    bne .loop
.done
    swap d1
    move.w #$0141,24(a1) ;'A', SERDAT
.waitforcharsentend
    btst #12,(a1) ;SERDATR TSRE, as we change serper
    beq .waitforcharsentend
    move.w d1,26(a1) ;SERPER
.waitforserialend
    btst #14,(a1) ;SERDATR RBF
    beq .waitforserialend
    move.w #$0800,132(a1) ;INTREQ RBF clear
    rts
