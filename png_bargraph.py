# -*- coding: utf-8 -*-
from __future__ import division
import struct
import zlib

def yield_block(header, data):
    assert len(header)==4, 'header must be 4 bytes!'
    # length:
    yield struct.pack('! L', len(data))
    # chunk type, 4 byte header
    yield header
    # data
    yield data
    # crc
    yield struct.pack(
        '! L',
        zlib.crc32("".join([header, data])) & 0xffffffff)
        
        
def make_bar_png(data, dmax='auto'):
    def make_line(line):
        r = [0xFF] * (line // 8)
        remaining_zeros = 8 - line % 8
        if remaining_zeros != 8:
            r.append(0xff ^ ((1 << remaining_zeros) - 1))
        r += [0x00] * (bytes_per_line - len(r))
        return r
        
    if dmax=='auto':
        dmax = max(data)
    bytes_per_line = (dmax+7) // 8
    width = dmax  
    height = len(data)
    bit_depth = 1
    color_type = 0  # grayscale
    compression_method, filter_method, interlace_method = 0, 0, 0
    yield bytearray([0x89, 'P', 'N', 'G', '\r', '\n', 0x1A, '\n'])
    # our header block
    for b in yield_block('IHDR', 
                         struct.pack('! LLBBBBB',
                                     width, height, bit_depth,
                                     color_type, compression_method, 
                                     filter_method, interlace_method)):
        yield b
    #unfiltered data (start with 0 as filterbyte)
    dat = [str(bytearray([0]+make_line(x))) for x in data]
    for b in yield_block('IDAT',
                         zlib.compress("".join(dat))):
        yield b
        
    for b in yield_block('IEND', ''):
        yield b
        
def test():
    import math
    with open('../pi.png', 'w') as f:
        dat = [int(x) for x in str(math.pi) if x != '.']
        for d in make_bar_png(dat):
            f.write(d)      
    
    import random
    with open('../random.png', 'w') as f:
        dat = [int(500**random.random()) for x in xrange(512)]
        for d in make_bar_png(dat):
            f.write(d)  

if __name__ == "__main__":
    test()               
                