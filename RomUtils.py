class RomUtils(object):
    ROMSIG512K = 0x11144ef9
    ROMSIG256K = 0x11114ef9
    romsig = {
        0x11114ef9: 256*1024,
        0x11144ef9: 512*1024
    }
    def __init__(self, **kwargs):
        amiga = kwargs["debugger"]
        self.amiga = amiga
        romaddr = 0xf80000
        romhdr = amiga.peek32(romaddr)
        romver = amiga.peek16(romaddr+12)
        romrev = amiga.peek16(romaddr+14)
        print(f"addr: {hex(romaddr)}, romhdr: {hex(romhdr)}, version: {romver}.{romrev}")
        if (not romhdr in self.romsig) or (self.romsig[romhdr] == 256*1024):
            romaddr = 0xfc0000
            romhdr = amiga.peek32(romaddr)
            romver = amiga.peek16(romaddr+12)
            romrev = amiga.peek16(romaddr+14)
            print(f"addr: {hex(romaddr)}, romhdr: {hex(romhdr)}, version: {romver}.{romrev}")
        romsize = self.romsig[romhdr]
        print(f"size: {hex(romsize)}")
        if (romaddr + romsize) > 0x1000000:
            raise ValueError("ROM continues past 24bit address space?!")
        self.ver = romver
        self.rev = romrev
        self.addr = romaddr
        self.size = romsize
        return
    def getaddr(self):
        return self.addr
    def getsize(self):
        return self.size
    def getversion(self):
        return self.ver
    def getrevision(self):
        return self.rev
