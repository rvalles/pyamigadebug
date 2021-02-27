import sys
import struct
sys.path.append('./')
from Crc import Crc
def decodeamigamfm(odd, even):
    mask = 0x55555555
    if len(odd) != len(even):
        raise ValueError()
    if len(odd)%4:
        raise ValueError()
    data = bytearray()
    for i in range(0, len(odd), 4):
        oddlong = struct.unpack(">I", odd[i:i+4])[0]
        evenlong = struct.unpack(">I", even[i:i+4])[0]
        datalong = (evenlong&mask)|((oddlong&mask)<<1);
        data += struct.pack(">I", datalong)
    return bytes(data)
def splitamigatrack(trackdata):
    found = trackdata.split(b"\x44\x89\x44\x89")
    print(f"sectors found: {len(found)}")
    for sector in found:
        yield bytes(b"\xAA\xAA\xAA\xAA" + b"\x44\x89\x44\x89" + sector)
    return None
    #if len(tracks) > 1:
        #if tracks[0] != b'':
            #if tracks[0][0] != 0x55: #MFM from expected 0xFF
                #wrapdata = bytes(tracks[0])
                #tracks = tracks[1:]
                #tracks[-1] = bytes(tracks[-1] + wrapdata)
#def tracksectors(track):
    #sectorsize = 0x440
    #sectors = []
    #gap = b''
    #for i in range(0, len(track), sectorsize):
        #print(i)
        #print(hex(track[i]))
        #if (i+sectorsize) > len(track):
            #gap = track[i:len(track)]
        #else:
            #sector = track[i:i+sectorsize]
            #sectors.append(sector)
    #return sectors, gap
def main():
    with open("trackdumpX.raw", "rb") as fh:
        trackdata = fh.read()
    #tracks = trackdata.split(b"\x44\x89\x44\x89")
    sectors = splitamigatrack(trackdata)
    for (foundnum, sector) in enumerate(sectors):
        print(f'#{foundnum}, size {len(sector)}')
        info = decodeamigamfm(sector[8:12], sector[12:16])
        print(f'Sector Info: signature: {info[0]} track: {info[1]} sector: {info[2]} secleft: {info[3]}')
if __name__ == "__main__":
    main()
