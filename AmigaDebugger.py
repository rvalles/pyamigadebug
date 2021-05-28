import struct
class AmigaDebugger(object):
    def __init__(self):
        self.readmem = self._fallbackreadmem
        self.writemem = self._fallbackwritemem
        self.readstr = self._fallbackreadstr
        return
    def _fallbackreadmem(self, addr, size):
        print(f"AmigaDebugger Fallback readmem {addr} {size}")
        if not size:
            return b''
        startaddr = addr & ~1
        buf = b''
        for pos in range(startaddr, addr + size, 2):
            buf += struct.pack(">H", self.peek16(pos))
            if not pos % 0x1000:
                print(f'{pos:x}')
        return buf[(addr & 1):(addr & 1) + size]
    def _fallbackwritemem(self, addr, buf):
        print(f"AmigaDebugger Fallback writemem {addr} {len(buf)}")
        if not len(buf):
            return
        if(addr & 1):
            self.poke8(addr, buf[0])
            buf = buf[1:]
            addr += 1
        for (w, i) in [(buf[i:i + 2], i) for i in range(0, len(buf) - 1, 2)]:
            self.poke16(addr + i, struct.unpack(">H", w)[0])
        if len(buf) & 1:
            print(addr, len(buf), buf[-1:])
            self.poke8(addr + len(buf) - 1, buf[-1])
        return
    def _fallbackreadstr(self, addr):
        s = b''
        while c := self.peek8(addr):
            s += bytes([c])
            addr += 1
        return s
    def isreg(self, reg):
        if reg.lower() in ['a0', 'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'sp', 'pc', 'd0', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7']:
            return True
        return False
    def callargs(self, **kwargs):
        addr = kwargs["addr"]
        if "result" in kwargs:
            resultreg = kwargs["result"]
        else:
            resultreg = False
        if "time" in kwargs:
            timecall = kwargs["time"]
        else:
            timecall = False
        for (reg, value) in kwargs.items():
            if not self.isreg(reg):
                continue
            self.setreg(reg, value)
        if timecall:
            self.calltime(addr)
        else:
            self.call(addr)
        if resultreg:
            self.sync()
            value = self.getreg(resultreg)
            return value
        return
    def libcall(self, **kwargs):
        if "a6" in kwargs or "addr" in kwargs:
            raise ValueError()
        kwargs["addr"] = kwargs["base"]+kwargs["lvo"]
        kwargs["a6"] = kwargs["base"]
        return self.callargs(**kwargs)
    def speek32(self, addr):
        value = self.peek32(addr)
        if value >= (2**31):
            value -= 2**32
        return value
    def speek16(self, addr):
        value = self.peek16(addr)
        if value >= (2**15):
            value -= 2**16
        return value
    def speek8(self, addr):
        value = self.peek8(addr)
        if value >= (2**7):
            value -= 2**8
        return value
    def getregs(self, regs):
        values = []
        for reg in regs:
            values.append((reg, self.getreg(reg)))
        return values
    def setregs(self, regs):
        for (reg, value) in regs:
            self.setreg(reg, value)
        return
    def dumpregs(self):
        regs = self.getregs(["pc", "a0", "a1", "a2", "a3", "a4", "a5", "a6", "sp","d0", "d1", "d2", "d3", "d4", "d5", "d6", "d7"])
        print(regs)
        return
