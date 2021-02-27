import shelve
import pathlib
from Crc import Crc
class AmigaSnippets(object):
    def __init__(self, **kwargs):
        if not "allocmem" in kwargs or not "debugger" in kwargs:
            raise ValueError()
        self.allocmem = kwargs["allocmem"]
        self.amiga = kwargs["debugger"]
        if "dbpath" in kwargs:
            self.dbpath = kwargs["dbpath"]
        else:
            self.dbpath = False
        self.debug = False
        if "debug" in kwargs:
            self.debug = kwargs["debug"]
        self.serial = False
        if "serial" in kwargs:
            self.serial = kwargs["serial"]
        if self.dbpath:
            self.snips = shelve.open(self.dbpath)
        else:
            self.snips = {}
        self.reusing = True if len(self.snips) else False
        self.crc = Crc(model="CRC-32/ISO-HDLC", reciprocal=True)
        self.verifyupload = False
        self.verifyuse = False
        self.execlib = False
        if "execlib" in kwargs:
            self.execlib = kwargs["execlib"]
        if "serper" in kwargs:
            self.serper = kwargs["serper"]
        else:
            self.serper = 29
        if "baudrate" in kwargs:
            self.baudrate = kwargs["baudrate"]
        else:
            self.baudrate = 115200
        #read/write mem can have separate speeds.
        if "readmemserper" in kwargs:
            self.readmemserper = kwargs["readmemserper"]
        else:
            self.readmemserper = self.serper
        if "readmembaudrate" in kwargs:
            self.readmembaudrate = kwargs["readmembaudrate"]
        else:
            self.readmembaudrate = self.baudrate
        if "writememserper" in kwargs:
            self.writememserper = kwargs["writememserper"]
        else:
            self.writememserper = self.serper
        if "writemembaudrate" in kwargs:
            self.writemembaudrate = kwargs["writemembaudrate"]
        else:
            self.writemembaudrate = self.baudrate
        #requisites for readwritemem.
        if self.serial and self.execlib:
            readwritemem = True
        else:
            readwritemem = False
        if "readwritemem" in kwargs:
            readwritemem = kwargs["readwritemem"]
        if readwritemem and (not self.serial or not self.execlib):
            raise ValueError("readwritemem snippets require a serial port.")
        if readwritemem:
            if self.amiga.debugger == "RomWack":
                self.readmem_threshold = 321
                self.writemem_threshold = 137
            elif self.amiga.debugger == "SAD":
                self.readmem_threshold = 138
                self.writemem_threshold = 146
            else:
                self.readmem_threshold = 128
                self.writemem_threshold = 128
            self.memrecv = self.getaddrfile("asm/memrecv.o")
            self.amiga.writemem = self.writemem
            self.memsend = self.getaddrfile("asm/memsend.o")
            #self.memsend = self.getaddrfile("asm/memsend_bne.o")
            self.amiga.readmem = self.readmem
        needcrc = False
        if "verifyupload" in kwargs:
            if kwargs["verifyupload"]:
                needcrc = True
        if "verifyuse" in kwargs:
            if kwargs["verifyuse"]:
                needcrc = True
        if needcrc:
            amigacrc = "asm/crc32.o"
            self.amigacrc = self.getaddrfile(amigacrc)
        if "verifyupload" in kwargs:
            self.verifyupload = kwargs["verifyupload"]
        if "verifyuse" in kwargs:
            self.verifyuse = kwargs["verifyuse"]
        return
    def keysum(self, data):
        return self.crc.crc(data)
    def amigakeysum(self, addr, size):
        amigasum = self.amiga.callargs(addr=self.amigacrc, a0=addr, d0=size, result="d0")
        return amigasum
    def getaddr(self, data):
        keysum = self.keysum(data)
        key = str(keysum)
        if key in self.snips:
            (addr, allocsize) = self.snips[key]
        else:
            addr = None
        if addr and self.verifyuse:
            if self.amigakeysum(addr, len(data)) != keysum:
                print("Snippet exists, but Amiga crc does not match. Reuploading to new allocation.")
                addr = None
            else:
                if self.debug:
                    print("Snippet exists, Amiga crc verified.")
        if addr:
            return addr
        addr = self.upload(data)
        if self.verifyupload:
            amigasum = self.amigakeysum(addr, len(data)) 
            if amigasum != keysum:
                print(f"Upload verify FAILED. key: {hex(keysum)}, amiga: {hex(amigasum)}.")
                return None
            else:
                if self.debug:
                    print("Upload verified.")
        self.snips[key] = (addr, len(data))
        return addr
    def upload(self, data):
        addr = self.allocmem(len(data), 0)
        self.amiga.writemem(addr, data)
        return addr
    def getaddrfile(self, path):
        with open(pathlib.Path(path), "rb") as f:
            data = f.read()
        addr = self.getaddr(data)
        if self.debug:
            print(f'snip getaddrfile() @ {hex(addr)} path: {path}')
        return addr
    def getaddrstr(self, strdata):
        bdata = strdata.encode("ascii") + b"\0"
        addr = self.getaddr(bdata)
        if self.debug:
            if len(strdata) < 40:
                print(f'snip getaddrstr() @ {hex(addr)} len {len(strdata)} str {strdata}.')
            else:
                print(f'snip getaddrstr() @ {hex(addr)} len {len(strdata)}.')
        return addr
    def _readmem(self, addr, size):
        ser = self.serial
        if self.debug:
            print(f"snip readmem: addr: {hex(addr)} size: {hex(size)}")
        serper = self.readmemserper | (self.amiga.serper << 16)
        self.amiga.callargs(addr=self.memsend, a0=addr, d0=size, d1=serper)
        ser.baudrate = self.readmembaudrate
        ser.write(b"S")
        ser.flush()
        data = ser.read(size)
        ser.baudrate = self.amiga.baudrate
        ser.write(b"F")
        ser.flush()
        self.amiga.sync()
        return data
    def readmem(self, addr, size):
        if size == 0:
            return b''
        if size < self.readmem_threshold:
            return self.amiga._readmem(addr, size)
        return self._readmem(addr, size)
    def verifiedreadmem(self, addr, size):
        data = self.amiga.readmem(addr, size)
        if self.amigakeysum(addr, size) != self.keysum(data):
            raise BufferError("CRC doesn't match after transfer.")
        return data
    def _writemem(self, addr, data):
        ser = self.serial
        if self.debug:
            print(f"snip writemem: addr: {hex(addr)} size: {hex(len(data))}")
        serper = self.writememserper | (self.amiga.serper << 16)
        self.amiga.callargs(addr=self.memrecv, a0=addr, d0=len(data), d1=serper)
        #ser.stopbits = 1
        ser.baudrate = self.writemembaudrate
        ser.write(b"S")
        ser.flush()
        while ser.read(1) != b'S':
            print("W", end='')
            pass
        ser.write(data)
        ser.flush()
        while ser.read(1) != b'A':
            print("W", end='')
            pass
        ser.baudrate = self.amiga.baudrate
        ser.write(b"F")
        ser.flush()
        self.amiga.sync()
        return
    def writemem(self, addr, data):
        size = len(data)
        if size == 0:
            return
        if size < self.writemem_threshold:
            return self.amiga._writemem(addr, data)
        return self._writemem(addr, data)
    def verifiedwritemem(self, addr, data):
        self.amiga.writemem(addr, data)
        if self.amigakeysum(addr, len(data)) != self.keysum(data):
            raise BufferError("CRC doesn't match after transfer.")
        return
    def freeall(self):
        for (addr, size) in self.snips.values():
            self.execlib.FreeMem(addr, size)
        self.snips.clear()
        return
