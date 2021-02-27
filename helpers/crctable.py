import sys
sys.path.append('./')
from Crc import Crc
#output table as 68k assembly data block
def outputdc32(lut, rowvals=6):
  for (idx, value) in enumerate(lut):
    if not idx%rowvals:
      print()
      print("    dc.l ", end='')
    print(f'${value:08x}', end='')
    if idx%rowvals != rowvals-1:
      print(',', end='')
  print(' ', end='')
  print()
def outputdc16(lut, rowvals=8):
  for (idx, value) in enumerate(lut):
    if not idx%rowvals:
      print()
      print("    dc.w ", end='')
    print(f'${value:04x}', end='')
    if idx%rowvals != rowvals-1:
      print(',', end='')
  print(' ', end='')
  print()
#def sanitytest():
  ##crc32
  #lut = createcrclut(reciprocal=True, width=32, poly=0x04c11db7, init=0xffffffff, refin=True, refout=True, xorout=0xffffffff, check=0xcbf43926, residue=0xdebb20e3, name="CRC-32/ISO-HDLC")
  ##crc32c
  #lut = createcrclut(reciprocal=True, width=32, poly=0x1edc6f41, init=0xffffffff, refin=True, refout=True, xorout=0xffffffff, check=0xe3069283, residue=0xb798b438, name="CRC-32/ISCSI")
  ##crc16-ccitt
  #lut = createcrclut(reciprocal=True, width=16, poly=0x1021, init=0x0000, refin=True, refout=True, xorout=0x0000, check=0x2189, residue=0x0000, name="CRC-16/KERMIT")
  #lut = createcrclut(reciprocal=True, width=16, poly=0x1021, init=0x0000, refin=False, refout=False, xorout=0x0000, check=0x31c3, residue=0x0000, name="CRC-16/XMODEM")
  #lut = createcrclut(reciprocal=True, width=8, poly=0xa7, init=0x00, refin=True, refout=True, xorout=0x00, check=0x26, residue=0x00, name="CRC-8/BLUETOOTH")
  #lut = createcrclut(reciprocal=True, width=8, poly=0x07, init=0x00, refin=False, refout=False, xorout=0x00, check=0xf4, residue=0x00, name="CRC-8/SMBUS")
  #lut = createcrclut(reciprocal=True, width=10, poly=0x233, init=0x000, refin=False, refout=False, xorout=0x000, check=0x199, residue=0x000, name="CRC-10/ATM")
  #lut = createcrclut(reciprocal=True, width=3, poly=0x3, init=0x0, refin=False, refout=False, xorout=0x7, check=0x4, residue=0x2, name="CRC-3/GSM")
  #lut = createcrclut(reciprocal=True, width=82, poly=0x0308c0111011401440411, init=0x000000000000000000000, refin=True, refout=True, xorout=0x000000000000000000000, check=0x09ea83f625023801fd612, residue=0x000000000000000000000, name="CRC-82/DARC")
def main():
  #sanitytest()
  crc = Crc("CRC-32/ISO-HDLC", reciprocal=True)
  outputdc32(crc.lut)
if __name__ == "__main__":
  main()
