import struct
import socket
class NBDServer(object):
    NBD_CMD_READ = 0
    NBD_CMD_WRITE = 1
    NBD_CMD_DISC = 2
    NBD_INIT_PASSWD = b'NBDMAGIC'
    NBD_INIT_IHAVEOPT = b'IHAVEOPT'
    NBD_CLISERV_MAGIC = bytes([0, 0x42, 0x02, 0x81, 0x86, 0x12, 0x53])
    NBD_REPLY_MAGIC = 0x3e889045565a9
    NBD_SIMPLE_REPLY_MAGIC = 0x67446698
    NBD_REQUEST_MAGIC = 0x25609513
    #handshake flags
    NBD_FLAG_FIXED_NEWSTYLE = 1
    NBD_FLAG_NO_ZEROES = 1<<1
    #transmission flags
    NBD_FLAG_HAS_FLAGS = 1
    NBD_FLAG_READ_ONLY = 1<<1
    NBD_FLAG_SEND_FLUSH = 1<<2
    NBD_FLAG_SEND_FUA = 1<<3
    NBD_FLAG_ROTATIONAL = 1<<4
    NBD_FLAG_SEND_TRIM = 1<<5
    NBD_FLAG_SEND_WRITE_ZEROES = 1<<6
    NBD_FLAG_SEND_DF = 1<<7
    NBD_FLAG_CAN_MULTI_CONN = 1<<8
    NBD_FLAG_SEND_RESIZE = 1<<9
    NBD_FLAG_SEND_CACHE = 1<<10
    NBD_FLAG_SEND_FAST_ZERO = 1<<11
    #option types
    NBD_OPT_EXPORT_NAME = 1
    NBD_OPT_ABORT = 2
    NBD_OPT_LIST = 3
    NBD_OPT_PEEK_EXPORT = 4
    NBD_OPT_STARTTLS = 5
    NBD_OPT_INFO = 6
    NBD_OPT_GO = 7
    NBD_OPT_STRUCTURED_REPLY = 8
    NBD_OPT_LIST_META_CONTEXT = 9
    NBD_OPT_SET_META_CONTEXT = 10
    #option reply types
    NBD_REP_ACK = 1
    NBD_REP_SERVER = 2
    NBD_REP_INFO = 3
    NBD_REP_META_CONTEXT = 4
    NBD_REP_ERR_UNSUP = 2**31 + 1
    NBD_REP_ERR_POLICY = 2**31 + 2
    NBD_REP_ERR_INVALID = 2**31 + 3
    NBD_REP_ERR_PLATFORM = 2**31 + 4
    NBD_REP_ERR_TLS_REQD = 2**31 + 5
    NBD_REP_ERR_UNKNOWN = 2**31 + 6
    NBD_REP_ERR_SHUTDOWN = 2**31 + 7
    NBD_REP_ERR_BLOCK_SIZE_REQD = 2**31 + 8
    NBD_REP_ERR_TOO_BIG = 2**31 + 9
    #information types (for NBD_REP_INFO)
    NBD_INFO_EXPORT = 0
    NBD_INFO_NAME = 1
    NBD_INFO_DESCRIPTION = 2
    NBD_INFO_BLOCK_SIZE = 3
    def __init__(self, **kwargs):
        if (not "read" in kwargs) or (not "write" in kwargs) or (not "disksize" in kwargs):
            raise ValueError()
        self.debug = False
        if "debug" in kwargs:
            self.debug = kwargs["debug"]
        self.read = kwargs["read"]
        self.write = kwargs["write"]
        self.disksize = kwargs["disksize"]
        return
    def handshake_oldstyle(self, conn, disksize):
        conn.send(self.NBD_INIT_PASSWD)
        conn.send(self.NBD_CLISERV_MAGIC)
        conn.send(struct.pack('>Q', disksize))
        conn.send(bytes(4)) #flags
        conn.send(bytes(124)) #reserved
        return
    def handshake_fixednewstyle(self, conn, disksize):
        transmissionflags = self.NBD_FLAG_HAS_FLAGS
        handshakeflags = self.NBD_FLAG_FIXED_NEWSTYLE
        conn.send(self.NBD_INIT_PASSWD)
        conn.send(self.NBD_INIT_IHAVEOPT)
        conn.send(struct.pack('>H', handshakeflags))
        clientflags = struct.unpack('>I', conn.recv(4))[0]
        if self.debug:
            print(f'NBD client flags: {clientflags}')
        while True:
            clientihaveopts = conn.recv(8)
            if clientihaveopts!=self.NBD_INIT_IHAVEOPT:
                print(f'NBD client IHAVEOPT was nonsense: {clientihaveopts}')
            clientopt = struct.unpack('>I', conn.recv(4))[0]
            clientoptsize = struct.unpack('>I', conn.recv(4))[0]
            if self.debug:
                print(f'NBD client opt: {clientopt} size: {clientoptsize}')
            clientoptparam = conn.recv(clientoptsize)
            if self.debug:
                print(f'NBD client opt param: {clientoptparam}')
            if clientopt == self.NBD_OPT_EXPORT_NAME:
                if self.debug:
                    print(f'NBD client sent NBD_OPT_EXPORT_NAME.')
                conn.send(struct.pack('>Q', disksize))
                conn.send(struct.pack('>H', transmissionflags)) #transmission flags
                conn.send(bytes(124)) #reserved
                break
            else:
                print(f'NBD replying NBD_REP_ERR_UNSUP at unknown client option: {clientopt}.')
                conn.send(struct.pack(">Q", self.NBD_REPLY_MAGIC))
                conn.send(struct.pack('>I', clientopt))
                conn.send(struct.pack('>I', self.NBD_REP_ERR_UNSUP))
                conn.send(bytes(4)) #reply length = 0
        return
    def server(self, host, port):
        #FIXME: TCP_NODELAY
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((host, port))
            sock.listen(1)
            conn, addr = sock.accept()
            with conn:
                print(f'Client {addr} connected')
                #self.handshake_oldstyle(conn, self.disksize)
                self.handshake_fixednewstyle(conn, self.disksize)
                sreq = '>IHHQQI'
                while True:
                    #print(conn.recv(1))
                    (magic, cmdflags, cmdtype, handle, offset, length) = struct.unpack(sreq, conn.recv(struct.calcsize(sreq)))
                    if self.debug:
                        print(f'NBD req magic: {hex(magic)}, cmdflags: {cmdflags}, type: {cmdtype},  handle: {hex(handle)}, offset: {offset}, length: {length}.')
                    if magic != self.NBD_REQUEST_MAGIC:
                        print(f'NBD req wrong request magic: {magic}.')
                        break
                    if cmdtype == self.NBD_CMD_READ:
                        if self.debug:
                            print("NBD NBD_CMD_READ")
                        data = self.read(offset, length)
                        conn.send(struct.pack('>I', self.NBD_SIMPLE_REPLY_MAGIC))
                        conn.send(bytes(4)) #error
                        conn.send(struct.pack('>Q', handle))
                        conn.send(data)
                    elif cmdtype == self.NBD_CMD_WRITE:
                        if self.debug:
                            print("NBD NBD_CMD_WRITE")
                        data = bytearray()
                        while len(data) < length:
                            data += conn.recv(length-len(data))
                        self.write(offset, data)
                        conn.send(struct.pack('>I', self.NBD_SIMPLE_REPLY_MAGIC))
                        conn.send(bytes(4)) #error
                        conn.send(struct.pack('>Q', handle))
                    elif cmdtype == self.NBD_CMD_DISC:
                        if self.debug:
                            print("NBD NBD_CMD_DISC")
                        break
                    else:
                        print(f'NBD unsupported type: {cmdtype}.')
            return
