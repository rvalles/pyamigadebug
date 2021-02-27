#!/usr/bin/env python3
import sys
import struct
def bbchecksum(data):
  cksum = 0
  mask = (1<<32)-1
  for i in struct.unpack('>256I', data):
    cksum += i
    if cksum > mask:
      cksum += 1
      cksum &= mask
  cksum = (~cksum) & mask
  return cksum
def main():
  if len(sys.argv) != 3:
    print("Need two arguments: Filename of assembled bootblock object and target file.")
    exit(1)
  srcpath = sys.argv[1]
  dstpath = sys.argv[2]
  with open(srcpath, "rb") as f:
    bootblock = bytearray(f.read())
  if bootblock[0:3] != b'DOS':
    print("Error: Bootblock signature missing.")
    exit(2)
  bootblock += bytes(1024 - len(bootblock))
  bootblock[4:8] = bytes(4)
  cksum = bbchecksum(bootblock)
  print(f"Bootblock checksum: {hex(cksum)}")
  bootblock[4:8] = struct.pack(">I", cksum)
  with open(dstpath, "wb") as f:
    f.write(bootblock)
  return 0
if __name__ == "__main__":
  main()
