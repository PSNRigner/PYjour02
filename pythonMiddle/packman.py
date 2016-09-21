from struct import *


def ushort_uint(buffer):
    return unpack('>HI', buffer)


def buf2latin(buffer):
    length = unpack(">H", buffer[0:2])[0]
    return length, unpack("%ds" % length, buffer[2:])[0].decode('latin1')


def ascii2buf(*args):
    buffer = b''
    for i in args:
        buffer = pack('>%dsH%ds' % (len(buffer), len(i)), buffer, len(i), i.encode())
    return pack('>I%ds' % len(buffer), len(args), buffer)
