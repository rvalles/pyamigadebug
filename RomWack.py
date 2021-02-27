#import sys
from AmigaDebugger import AmigaDebugger
import re
import time
import struct
class RomWack(AmigaDebugger):
    def __init__(self, **kwargs):
        super().__init__()
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
        self.debugger = "RomWack"
        self.regsre1 = re.compile(r'PC: ([0-9A-F]{6,8}) +SR: ([0-9A-F]{4}) +USP: ([0-9A-F]{6,8}) +SSP: ([0-9A-F]{6,8}) +(XCPT|TRAP)+: ([0-9A-F]{4}) +TASK: ([0-9A-F]{6,8})')
        self.regsre2 = re.compile(r'DR:+((?: [0-9A-F]{8}){8})')
        self.regsre3 = re.compile(r'AR:+((?: [0-9A-F]{8}){7})')
        self.readmem = self._readmem
        self.writemem = self._writemem
        self.serper = 372 #romwack rawioinit() puts 372 in SERPER
        self.baudrate = 9600
        self.serial.baudrate = self.baudrate
        self.sync()
        self.execdebug = self.peek32(0x4) - 114
        return
    def sync(self):
        while self.serial.in_waiting:
            self.serial.read(1)
        while True:
            if self.serial.in_waiting:
                if self.serial.read(1) == b'_':
                    break
                else:
                    continue
            time.sleep(0.01)
            self.serial.write(b'_')
            self.serial.flush()
            if self.syncabort:
                if self.syncabort.is_set():
                    exit(1)
        while self.serial.in_waiting:
            self.serial.read(1)
        self.serial.write(b'\r')
        self.serial.flush()
        while self.serial.read(1) != b'\n':
            pass
        while self.serial.read(1) != b'\n':
            pass
        return
    def getmachinestate(self):
        machinestate = {}
        self.serial.write(b'regs\r')
        self.serial.readline()
        regs = self.serial.readline().decode()
        (machinestate["pc"], machinestate["sr"], machinestate["usp"], machinestate["ssp"], machinestate["xcpt"], machinestate["task"]) = [int(x, 16) for x in self.regsre1.match(regs).group(1, 2, 3, 4, 6, 7)]
        regs = self.serial.readline().decode()
        machinestate["d"] = [int(x, 16) for x in self.regsre2.match(regs).group(1).split(' ')[1:]]
        regs = self.serial.readline().decode()
        machinestate["a"] = [int(x, 16) for x in self.regsre3.match(regs).group(1).split(' ')[1:]]
        regs = self.serial.readline().decode()
        return machinestate
    def peek16(self, addr):
        self.serial.write(b':2\r')
        self.serial.readline()
        self.serial.readline()
        self.serial.write(f'{hex(addr)[2:]}\r'.encode("ascii"))
        self.serial.readline()
        value = int(self.serial.readline().split(b' ')[1], 16)
        return value
    def poke16(self, addr, value):
        self.serial.write(b':0\r')
        self.serial.readline()
        self.serial.write(f'{hex(addr)[2:]}\r'.encode("ascii"))
        self.serial.readline()
        self.serial.write(b'=')
        self.serial.flush()
        while self.serial.read(1) != b'=':
            pass
        self.serial.write(f'{value:0>4x}\r'.encode("ascii"))
        self.serial.readline()
        return
    def peek32(self, addr):
        self.serial.write(b':4\r')
        self.serial.readline()
        self.serial.readline()
        self.serial.write(f'{hex(addr)[2:]}\r'.encode("ascii"))
        self.serial.readline()
        value = int(b"".join(self.serial.readline().split(b' ')[1:3]), 16)
        return value
    def poke32(self, addr, value):
        self.serial.write(b':0\r')
        self.serial.readline()
        self.serial.write(f'{hex(addr)[2:]}\r'.encode("ascii"))
        self.serial.readline()
        self.serial.write(b'alter\r')
        while (ch := self.serial.read(1)) != b'=':
            pass
        word = value >> 16
        self.serial.write(f'{word:0>4x}\r'.encode("ascii"))
        while self.serial.read(1) != b'=':
            pass
        word = value & 0xFFFF
        self.serial.write(f'{word:0>4x}\r'.encode("ascii"))
        while self.serial.read(1) != b'=':
            pass
        self.serial.write(b'\r')
        self.serial.readline()
        return
    def peek8(self, addr):
        if addr & 1:
            value = self.peek16(addr & 0xFFFFFFFE) & 0xFF
        else:
            value = self.peek16(addr) >> 8
        return value
    def poke8(self, addr, value):
        self.serial.write(b':4\r')
        self.serial.readline()
        self.serial.readline()
        if addr & 1:
            self.serial.write(f'{hex(addr&0xFFFFFFFE)[2:]}\r'.encode("ascii"))
            self.serial.readline()
        else:
            self.serial.write(f'{hex(addr)[2:]}\r'.encode("ascii"))
            self.serial.readline()
        old = self.serial.readline().split(b' ')[1]
        if addr & 1:
            new = old[:2] + "{0:0>2x}".format(value).encode("ascii")
        else:
            new = "{0:0>2x}".format(value).encode("ascii") + old[2:]
        self.serial.write(b'=')
        self.serial.flush()
        while self.serial.read(1) != b'=':
            pass
        self.serial.write(new + b'\r')
        self.serial.readline()
        self.serial.readline()
        return
    def _readmem(self, addr, size):
        words = 0
        start = addr & ~1
        end = addr + size
        end += end & 1
        totalwords = (end - start) // 2
        if addr & 1 and not size & 1:
            workaround = 1
        else:
            workaround = 0
        self.serial.write(b':0\r')
        self.serial.readline()
        self.serial.write(f'{hex(addr)[2:]}\r'.encode("ascii"))
        self.serial.readline()
        buf = b''
        self.serial.write(f':{hex(size+workaround)[2:]}\r'.encode("ascii"))
        self.serial.readline()
        for i in range(0, totalwords // 8):
            words = self.serial.readline().split(b' ')[1:]
            for j in range(0, 8):
                value = int(words[j], 16)
                buf += struct.pack(">H", value)
        remainingwords = totalwords % 8
        if remainingwords:
            words = self.serial.readline().split(b' ')[1:]
            for j in range(0, remainingwords):
                value = int(words[j], 16)
                buf += struct.pack(">H", value)
        self.serial.write(b':0\r')
        self.serial.readline()
        if start != addr:
            buf = buf[1:]
        if len(buf) == (size + 1):
            buf = buf[:-1]
        return buf
    def _writemem(self, addr, buf):
        size = len(buf)
        endaddr = addr + size
        if self.debug:
            print(f"romwack writemem {addr} {size}")
        if(addr & 1):
            self.poke8(addr, buf[0])
            buf = buf[1:]
            addr += 1
        self.serial.write(b':0\r')
        self.serial.readline()
        self.serial.write(f'{hex(addr)[2:]}\r'.encode("ascii"))
        self.serial.readline()
        self.serial.write(b'alter\r')
        self.serial.readline()
        for word in [buf[i:i + 2] for i in range(0, len(buf) - 1, 2)]:
            word = struct.unpack(">H", word)[0]
            while self.serial.read(1) != b'=':
                pass
            self.serial.write(f'{word:0>4x}\r'.encode("ascii"))
            addr += 2
            self.serial.readline()
        while self.serial.read(1) != b'=':
            pass
        self.serial.write(b'\r')
        self.serial.readline()
        if addr != endaddr:
            if self.debug:
                print(f'romwack writemem even end poke8: {hex(addr)} {hex(endaddr)} {hex(buf[-1])}')
            self.poke8(addr, buf[-1])
        return
    def getreg(self, reg):
        if reg.lower() == "a7" or reg.lower() == "sp":
            reg = "u"
        self.serial.write(f'!{reg}'.encode("ascii"))
        self.serial.flush()
        buf = b""
        while (c := self.serial.read(1)) != b'=':
            buf += c
        self.serial.write(b'\r')
        self.serial.readline()
        value = int(buf.split(b' ')[1].decode("ascii"), 16)
        return value
    def setreg(self, reg, value):
        if reg.lower() == "a7" or reg.lower() == "sp":
            reg = "u"
        self.serial.write(f'!{reg}'.encode("ascii"))
        self.serial.flush()
        while self.serial.read(1) != b'=':
            pass
        self.serial.write(f'{value:0>8x}\r'.encode("ascii"))
        self.serial.readline()
        return
    def go(self, addr):
        while self.serial.in_waiting:
            print(self.serial.read(1), end='')
        self.serial.write(b':0\r')
        self.serial.readline()
        self.serial.write(f'{hex(addr)[2:]}\r'.encode("ascii"))
        self.serial.readline()
        self.serial.write(b'go\r')
        while self.serial.read(1) != b'o':
            pass
        return
    def __call(self, addr):
        if self.debug:
            print(f"RomWack calling {hex(addr)}.")
        sp = self.getreg("sp") - 4
        self.setreg("sp", sp)
        self.poke32(sp, self.execdebug)
        self.go(addr)
        return
    def call(self, addr):
        self.__call(addr)
        return
    def calltime(self, addr):
        self.__call(addr)
        start = time.monotonic()
        print(f'Call start: {start}s')
        while not self.serial.in_waiting:
            pass
        end = time.monotonic()
        print(f'Call end: {end}s\ndiff {end-start}s')
        return
    def resume(self):
        self.serial.write(b'resume\r')
        self.serial.read(6)
        return
    def reboot(self):
        self.serial.write(b'ig\r')
        self.serial.read(2)
        return
