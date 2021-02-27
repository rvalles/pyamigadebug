_LVODebug equ -114
debugloop:
    movea.l $4, a6
    jsr _LVODebug(a6)
    bra debugloop
even
.oldsp
    dc.l $0
.oldpc
    dc.l $0
.signature
    dc.l $DEB10070
