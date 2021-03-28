from AmigaDebugger import AmigaDebugger
import time
import struct
import traceback
class SAD(AmigaDebugger):
    sadcmdbook = [("ALLOCATE_MEMORY", 0x0A),
                ("CALL_ADDRESS", 0x07),
                ("FREE_MEMORY", 0x0B),
                ("GET_CONTEXT_FRAME", 0x09),
                ("NOP", 0x00),
                ("READ_ARRAY", 0x0F),
                ("READ_BYTE", 0x04),
                ("READ_LONG", 0x06),
                ("READ_WORD", 0x05), #V40+
                ("RESET", 0x10),
                ("RETURN_TO_SYSTEM", 0x08),
                ("TURN_OFF_SINGLE", 0x0D),
                ("TURN_ON_SINGLE", 0x0C),
                ("WRITE_ARRAY", 0x0E),
                ("WRITE_BYTE", 0x01), #V40+
                ("WRITE_LONG", 0x03),
                ("WRITE_WORD", 0x02),
                ("INVALID", 0x77)
                ]
    SAD_USP = 12
    SAD_D0 = 16
    SAD_A0 = 48
    SAD_PC = 82
    def __init__(self, **kwargs):
        super().__init__()
        self.debugger = "SAD"
        if not "serial" in kwargs:
            raise ValueError()
        self.serial = kwargs["serial"]
        if "Debug" in kwargs:
            self.debug = kwargs["Debug"]
        else:
            self.debug = False
        if "syncabort" in kwargs: #Meant to be a threading.Event
            self.syncabort = kwargs["syncabort"]
        else:
            self.syncabort = False
        self.readmem = self._readmem
        self.writemem = self._writemem
        self.entry = None
        self.serper = 372
        self.baudrate = 9600
        self.serial.baudrate = self.baudrate
        #self.serial.stopbits = 1
        self._sync()
        self.sadbug = self.checksadbug()
        if self.sadbug and self.debug:
            print("Bugged SAD!!!")
        self.sadcmd = {name: struct.pack(">B", value - (1 if (self.sadbug and value) else 0)) for (name, value) in self.sadcmdbook}
        self.execdebug = self.peek32(0x4) - 114
        self._ctxframe = self._get_context_frame()
        return
    def _sync(self):
        self.serial.timeout=0.1
        while True:
            if self.syncabort:
                if self.syncabort.is_set():
                    exit(1)
            if (c := self.serial.read(1)) != b'S':
                #print(c)
                continue
            if self.serial.read(1) != b'A':
                continue
            if self.serial.read(1) != b'D':
                continue
            c = self.serial.read(1)
            if c == b'\xBF':
                self.entry = "NMI"
                break
            elif c == b'\x3F':
                self.entry = "Debug()"
                break
            elif c == b'\x21':
                self.entry = "Crash"
                break
            continue
        self.serial.timeout=None
        return
    def sync(self):
        self._sync()
        return
    def checksadbug(self):
        self.serial.write(b"\xAF\x05\x00\xFC\x00\x00")
        self.serial.flush()
        bugged = False
        response = self.serial.read(2)
        if self.debug:
            print(f"SAD test response: {response}")
        if response == b"\x00\x06":
            bugged = True
        self._sync()
        return bugged
    def _flush(self):
        while self.serial.in_waiting:
            while self.serial.in_waiting:
                self.serial.read(1)
            time.sleep(0.002)
    def peek32(self, addr):
        self._flush()
        self.serial.write(b'\xAF' + self.sadcmd['READ_LONG'])
        self.serial.write(struct.pack(">I", addr))
        self.serial.flush()
        ack = self.serial.read(2)
        res1 = self.serial.read(2)
        value = struct.unpack(">I", self.serial.read(4))[0]
        self._sync()
        return value
    def peek16(self, addr):
        if self.sadbug:
            valuebytes = self._readmem(addr, 2)
            value = struct.unpack(">H", valuebytes)[0]
            return value
        self._flush()
        self.serial.write(b'\xAF' + self.sadcmd['READ_WORD'])
        self.serial.write(struct.pack(">I", addr))
        self.serial.flush()
        ack = self.serial.read(2)
        res1 = self.serial.read(2)
        value = struct.unpack(">H", self.serial.read(2))[0]
        self._sync()
        return value
    def peek8(self, addr):
        self._flush()
        self.serial.write(b'\xAF' + self.sadcmd['READ_BYTE'])
        self.serial.write(struct.pack(">I", addr))
        self.serial.flush()
        ack = self.serial.read(2)
        res1 = self.serial.read(2)
        value = struct.unpack(">B", self.serial.read(1))[0]
        self._sync()
        return value
    def poke32(self, addr, value):
        self._flush()
        self.serial.write(b'\xAF' + self.sadcmd['WRITE_LONG'])
        self.serial.write(struct.pack(">I", addr))
        if value < 0:
            self.serial.write(struct.pack(">i", value))
        else:
            self.serial.write(struct.pack(">I", value))
        self.serial.flush()
        ack = self.serial.read(2)
        res1 = self.serial.read(2)
        self._sync()
        return
    def poke16(self, addr, value):
        self._flush()
        self.serial.write(b'\xAF' + self.sadcmd['WRITE_WORD'])
        self.serial.write(struct.pack(">I", addr))
        self.serial.write(struct.pack(">H", value))
        self.serial.flush()
        ack = self.serial.read(2)
        res1 = self.serial.read(2)
        self._sync()
        return
    def poke8(self, addr, value):
        if self.sadbug:
            valuebytes = struct.pack(">H", value)
            self._writemem(addr, valuebytes)
            return
        self._flush()
        self.serial.write(b'\xAF' + self.sadcmd['WRITE_BYTE'])
        self.serial.write(struct.pack(">I", addr))
        self.serial.write(struct.pack(">B", value))
        self.serial.flush()
        ack = self.serial.read(2)
        res1 = self.serial.read(2)
        self._sync()
        return
    def _readmem(self, addr, size):
        self._flush()
        self.serial.write(b'\xAF' + self.sadcmd['READ_ARRAY'])
        self.serial.write(struct.pack(">I", addr))
        self.serial.write(struct.pack(">I", size))
        self.serial.flush()
        ack = self.serial.read(2)
        res1 = self.serial.read(2)
        buf = self.serial.read(size)
        self._sync()
        return buf
    def _writemem(self, addr, buf):
        self._flush()
        self.serial.write(b'\xAF' + self.sadcmd['WRITE_ARRAY'])
        self.serial.write(struct.pack(">I", addr))
        self.serial.write(struct.pack(">I", len(buf)))
        self.serial.flush()
        ack = self.serial.read(2)
        self.serial.write(buf)
        self.serial.flush()
        res1 = self.serial.read(2)
        self._sync()
        return buf
    def nop(self):
        self._flush()
        self.serial.write(b'\xAF' + self.sadcmd['NOP'])
        self.serial.flush()
        return
    def _jsr(self, addr):
        self._flush()
        if self.debug:
            print(f"Calling {hex(addr)}.")
        self.serial.write(b'\xAF' + self.sadcmd['CALL_ADDRESS'])
        self.serial.write(struct.pack(">I", addr))
        self.serial.flush()
        ack = self.serial.read(2)
        return
    def resume(self):
        self._flush()
        self.serial.write(b'\xAF' + self.sadcmd['RETURN_TO_SYSTEM'] + b'\0\0\0\0')
        ack = self.serial.read(2)
        return
    def reboot(self):
        self._flush()
        self.serial.write(b'\xAF' + self.sadcmd['RESET'] + b'\xFF\xFF\xFF\xFF')
        ack = self.serial.read(1)
        return
    def go(self, addr):
        ctx = self._ctxframe
        self.poke32(ctx + self.SAD_PC, addr)
        self.resume()
        return
    def call(self, addr):
        if self.debug:
            print(f"SAD Calling {hex(addr)}.")
        sp = self.getreg("sp") - 8
        self.setreg("sp", sp)
        self.poke32(sp, self.execdebug)
        self.go(addr)
        return
    def _get_context_frame(self):
        self._flush()
        self.serial.write(b'\xAF' + self.sadcmd['GET_CONTEXT_FRAME'])
        self.serial.flush()
        ack = self.serial.read(2)
        res1 = self.serial.read(2)
        addr = struct.unpack(">I", self.serial.read(4))[0]
        if self.debug:
            print(f"Context frame at {hex(addr)}")
        self._sync()
        return addr
    def _getregaddr(self, reg):
        ctx = self._ctxframe
        if reg[0] == 'a':
            addr = ctx + self.SAD_A0 + int(reg[1]) * 4
        elif reg[0] == 'd':
            addr = ctx + self.SAD_D0 + int(reg[1]) * 4
        elif reg == "usp":
            addr = ctx + self.SAD_USP
        elif reg == "pc":
            addr = ctx + self.SAD_PC
        return addr
    def getreg(self, reg):
        self._flush()
        reg = reg.lower()
        if not self.isreg(reg):
            raise ValueError("Bad register name.")
        if reg == "a7" or reg == "sp":
            reg = "usp"
        addr = self._getregaddr(reg)
        value = self.peek32(addr)
        return value
    def setreg(self, reg, value):
        self._flush()
        reg = reg.lower()
        if not self.isreg(reg):
            raise ValueError("Bad register name.")
        if reg == "a7" or reg == "sp":
            reg = "usp"
        addr = self._getregaddr(reg)
        self.poke32(addr, value)
        return
