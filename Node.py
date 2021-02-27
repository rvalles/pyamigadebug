import struct
class Node(object):
    ln_Succ = 0
    ln_Pred = 4
    ln_Type = 8
    ln_Pri = 9
    ln_Name = 10
    lh_Head = 0
    lh_Tail = 4
    lh_TailPred = 8
    lh_Type = 12
    lh_Pad = 13
    #for LN_TYPE
    NT_UNKNOWN = 0
    NT_TASK = 1
    NT_INTERRUPT = 2
    NT_DEVICE = 3
    NT_MSGPORT = 4
    NT_MESSAGE = 5
    NT_FREEMSG = 6
    NT_REPLYMSG = 7
    NT_RESOURCE = 8
    NT_LIBRARY = 9
    NT_MEMORY = 10
    NT_SOFTINT = 11
    NT_FONT = 12
    NT_PROCESS = 13
    NT_SEMAPHORE = 14
    NT_SIGNALSEM = 15
    NT_BOOTNODE = 16
    NT_KICKMEM = 17
    NT_GRAPHICS = 18
    NT_DEATHMESSAGE = 19
    NT_USER = 254
    NT_EXTENDED = 255
    def nodes(self, ln):
        while True:
            lnsucc = self.amiga.peek32(ln + self.ln_Succ)
            if not lnsucc:
                break
            lnpred = self.amiga.peek32(ln + self.ln_Pred)
            if not lnpred:
                ln = lnsucc
                continue
            yield ln
            ln = lnsucc
    def nodeheaders(self, lh):
        for ln in self.nodes(lh):
            yield (ln, self.amiga.readmem(ln, 14))
    def nodeheader(self, ln):
        (lnsucc, lnpred, lntype, lnpri, lnname) = struct.unpack(">IIBBI", ln)
        return (lnsucc, lnpred, lntype, lnpri, lnname)
    def nodeheaderwithname(self, ln):
        (lnsucc, lnpred, lntype, lnpri, lnnameptr) = self.nodeheader(ln)
        lnname = self.amiga.readstr(lnnameptr)
        return (lnsucc, lnpred, lntype, lnpri, lnnameptr, lnname)
