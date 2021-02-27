**CRC-32/ISO-HDLC
*aka CRC-32, CRC-32/ADCCP, CRC-32/V-42, CRC-32/XZ, PKZIP
*a0 addr, d0 size. Returns crc32 in d0.
crc32:
    *a1 saved4, d1 crc, d2 value, d3 bit, d4 poly
    cmp.l #0,d0
    bne .prepare
    rts
.prepare
    movem.l d2-d3,-(sp)
    move.l d4,a1
    move.l .polynomy(pc),d4
    clr.l d1
    not.l d1 ;init = 0xFFFFFFFF
    sub.l #1,d0 ;for dbra
    bra .loop
.oloop
    swap d0
.loop
    clr.l d2
    move.b (a0)+,d2
    eor.b d1,d2
    move.w #7,d3
.iloop
    btst.l #0,d2
    beq .iloopfalse
    eor.l d4,d2
    lsr.l #1,d2
    bset.l #31,d2
    dbra d3,.iloop
    bra .iloopend
.iloopfalse
    lsr.l #1,d2
    dbra d3,.iloop
.iloopend
    lsr.l #8,d1
    eor.l d2,d1
    dbra d0,.loop
    swap d0
    dbra d0,.oloop
    eor.l d1,d0 ;xorout = 0xFFFFFFFF
    movem.l (sp)+,d2-d3
    move.l a1,d4
    rts
.polynomy
    *Reciprocal polynomy, as to avoid reflection and have less shifts, we use the reciprocal model.
    ifd crc32c
        echo "crc32c aka CRC-32/ISCSI polynomy selected."
        dc.l $05EC76F1
    else
        echo "crc32 aka CRC-32/ISO-HDLC polynomy selected."
        dc.l $DB710641
    endif
