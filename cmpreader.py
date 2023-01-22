#!/usr/bin/python3

# ********************************************
#  SWAT 3 CMP to WAV audio decompression tool
#  https://github.com/induktio/swat3-tools
# ********************************************
#
# Usage: ./cmpreader.py [-v] [-t] filename.cmp
#
# Input filenames must have .cmp extension for the tool to work.
# Converted audio files are written to 'output' directory in WAV format.
#
# Author: Induktio <admin@induktio.net>
#

import os
import sys
import wave
import struct
import argparse
from collections import deque


class BitReader:
    def __init__(self, f, verify=False):
        self.input = f
        self.bits = 0
        self.bcount = 0
        self.readbts = 0
        self.readcnt = 0
        self.verify_file = None
        if verify:
            try:
                log_file = f.name.replace('cmp', 'log')
                self.verify_file = open(log_file)
                print('Verifying log file: %s' % (log_file))
            except:
                print('Log file not found: %s' % (log_file))
                self.verify_file = None

    def readbit(self):
        if self.bcount == 0:
            a = self.input.read(4)
            if (len(a) > 0):
                self.bits = struct.unpack('<i', a)[0]
            else:
                raise RuntimeError
            self.bcount = 32
        rv = ( self.bits >> (32-self.bcount) ) & 1
        self.bcount -= 1
        return rv

    def verify(self, n, v):
        if self.verify_file:
            cn, cv = self.verify_file.readline().split()
            assert(int(cn) == n)
            assert(int(cv) == v)

    def readbits(self, n):
        v = 0
        if (self.readbts % 32) + n > 32 and n < 32:
            n1 = 32 - self.readbts % 32
            n2 = n - n1
            i = 0
            while i < n1:
                v |= (self.readbit() << i)
                i += 1
            i = 0
            v <<= n2
            while i < n2:
                v |= (self.readbit() << i)
                i += 1
        else:
            i = 0
            while i < n:
                v |= (self.readbit() << i)
                i += 1

        if n < 32:
            self.verify(n, v)
            self.readcnt += 1
            self.readbts += n
        return v


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('inputfile', type=str, default=None, help='note: input file must have .cmp extension')
    parser.add_argument('-t', '--test', action='store_true', help='verify extracted output using .log file')
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose output mode')
    args = parser.parse_args()

    inputfile = args.inputfile.replace('.cmp', '')
    r = BitReader(open('%s.cmp' % (inputfile), 'rb'), verify=args.test)

    r.readbits(64)
    len_coded = r.readbits(32)
    len_wav = r.readbits(32)
    sampling_freq = r.readbits(32)
    r.readbits(96)

    cache = deque()
    mov_sum = 0
    cur_len = 0
    border = 0
    samples = 0
    d1 = 0
    d2 = 0
    smp = 0

    if not os.access('output', os.R_OK):
        os.mkdir('output')
    wavout = wave.open('output/%s.wav' % (inputfile.split('/')[-1]), 'wb')
    wavout.setparams((1, 2, sampling_freq, int(len_wav/2), 'NONE', 'not compressed'))
    wavsamples = []

    while samples < len_wav/2:
        border = r.readbits(1)
        z = r.readbits(cur_len)

        if border == 1 and z == 0:
            cur_len = r.readbits(4)
        else:
            sign = 1
            if border: sign = -1
            d1 = z * sign
            d2 += d1
            smp += d2
            samples += 1
            cache.append(smp)
            mov_sum += smp
            if samples > 4096:
                mov_sum -= cache.popleft()

            drift = int(mov_sum / 4096.0 * min(samples, 1024) / 1024.0)
            wavsamples.append(struct.pack('h', max(-32768, min(32767, (smp-drift)<<5))))

    wavout.writeframes(b''.join(wavsamples))
    wavout.close()

    if args.verbose:
        print('samples_cmp: %d samples_wav: %d sampling_freq: %d ' % (len_coded, len_wav, sampling_freq))


