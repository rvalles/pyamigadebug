#To understand this, refer to "crc_v3.txt" (Ross Williams, 1993)
#https://archive.org/details/PainlessCRC
#ark:/13960/t75t59n0p
class Crc(object):
    def __init__(self, model="CRC-32/ISO-HDLC", reciprocal=True):
        self.name = model
        self.reciprocal = reciprocal
        #TODO: This is in lieu of referencing an external table from the reveng project
        if model == "CRC-32/ISO-HDLC":
            self.width = 32
            self.poly = 0x04c11db7
            self.init = 0xffffffff
            self.refin = True
            self.refout = True
            self.xorout = 0xffffffff
            self.check = 0xcbf43926
            self.residue = 0xdebb20e3
        elif model == "CRC-32/ISCSI":
            self.width = 32
            self.poly = 0x1edc6f41
            self.init = 0xffffffff
            self.refin = True
            self.refout = True
            self.xorout = 0xffffffff
            self.check = 0xe3069283
            self.residue = 0xb798b438
        elif model == "CRC-16/KERMIT":
            self.width = 16
            self.poly = 0x1021
            self.init = 0x0000
            self.refin = True
            self.refout = True
            self.xorout = 0x0000
            self.check = 0x2189
            self.residue = 0x0000
        elif model == "CRC-16/XMODEM":
            self.width = 16
            self.poly = 0x1021
            self.init = 0x0000
            self.refin = False
            self.refout = False
            self.xorout = 0x0000
            self.check = 0x31c3
            self.residue = 0x0000
        else:
            raise ValueError()
        if reciprocal:
            self.refin = not self.refin
            self.refout = not self.refout
            #Poly have an extra 1 in msb which is usually omitted, making them width+1.
            #This starts to matter when reflection happens.
            self.poly = (1 << self.width) | self.poly
            self.poly = self.reflect(self.poly, self.width) & ((1 << self.width) - 1)
            self.init = self.reflect(self.init, self.width)
            self.lut = list(self.crcmakelutref())
        else:
            self.lut = list(self.crcmakelut())
        self.selftest()
    def reflect(self, value, width):
        fmt = "{:0" + str(width) + "b}"
        return int(fmt.format(value)[::-1], 2)
    #works with 8 to 82 width
    def __crclut(self, data, lut, width, init, refin, refout, xorout):
        crc = init
        mask = ((1 << width) - 1)
        for b in data:
            if refin:
                b = self.reflect(b, 8)
            crc = (crc ^ (b << (width - 8)))
            idx = crc >> (width - 8)
            crc = (crc << 8) & mask
            crc ^= lut[idx]
        if refout:
            crc = self.reflect(crc, width)
        return crc ^ xorout
    #works with 3 to 82 width
    def __crcreflut(self, data, lut, width, init, refin, refout, xorout):
        crc = init
        for b in data:
            if refin:
                b = self.reflect(b, 8)
            idx = (crc ^ b) & 0xFF
            crc = (crc >> 8) ^ lut[idx]
        if refout:
            crc = self.reflect(crc, width)
        return crc ^ xorout
    def crc(self, data):
        if self.reciprocal:
            crc = self.__crcreflut(data, self.lut, self.width, self.init, self.refin, self.refout, self.xorout)
        else:
            crc = self.__crclut(data, self.lut, self.width, self.init, self.refin, self.refout, self.xorout)
        return crc
    def __crcmakelut(self, poly, width):
        topmask = 1 << (width - 1)
        for value in range(0x100):
            value = value << (width - 8)
            for bit in range(8):
                if value & topmask:
                    value <<= 1
                    value ^= poly
                else:
                    value <<= 1
                value &= ((1 << width) - 1)
            yield value
    def __crcmakelutref(self, poly):
        for value in range(0x100):
            for bit in range(8):
                if value & 1:
                    value ^= poly
                    value |= (1 << self.width)
                value >>= 1
            yield value
    def crcmakelut(self):
        return self.__crcmakelut(self.poly, self.width)
    def crcmakelutref(self):
        return self.__crcmakelutref(self.poly)
    def selftest(self):
        testdata = b"123456789"
        if (result := self.crc(testdata)) != self.check:
            raise AssertionError(f'crc Result {hex(result)} does not match Rocksoft check {hex(self.check)}')
