#!/usr/bin/env python
#-*- encoding: utf-8 -*-
import struct
import sys

SIGNATURE_SIZE = 8

COLOR_TYPES = {
    0: 'GrayScale',
    2: 'TrueColor',
    3: 'Indexed',
    4: 'AlphaGrayScale',
    6: 'AlphaTrueColor'
}

INTERLACE_METHODS = {
    0: 'NoInterlace',
    1: 'AdamInterlace'
}


def split_hex_string(hex_string):
    return ' '.join([hex_string[i:i+2] for i in range(0, len(hex_string), 2)])

class PNG_Parser():
    def __init__(self, path):
        self.buf = open(path, 'rb').read()
        self.signature = self.buf[0:SIGNATURE_SIZE]
        self.chunks = self.get_chunks()

    def summary(self):
        """
            Возвращает метаинформацию о файле
        """
        summary = 'Signature: %s\n' % split_hex_string(self.signature.encode('hex'))
        summary += 'Chunks: %d\n' % len(self.chunks)
        for chunk in self.chunks:
            summary += 'Type: %s, lenght: %d, crc32: %s\n' % (str(chunk['type']), chunk['length'], chunk['crc32'])
            if chunk['type'] == 'IHDR':
                summary += ('\tWidth: %d\n' + \
                    '\theight: %d\n' + \
                    '\tbit depth: %d\n' + \
                    '\tcolor type: %s\n' + \
                    '\tcompr method: %s\n' + \
                    '\tfilter method: %s\n' + \
                    '\tinterlace method: %s\n') % (self.parse_IHDR(chunk['content']))
        return summary

    def get_chunks(self):
        """
            Извлекает чанки (блоки данных, из которых состоит файл).
            Чанк состоит из четырех частей: длина (4 байта), тип (4 байта),
            содержимое (байтов поля длины) и контрольной суммы crc32
        """
        chunks = []
        i = SIGNATURE_SIZE
        while i < len(self.buf):
            chunk = {}
            chunk['length'] = struct.unpack_from('>I', self.buf, offset=i)[0]
            chunk['type'] = struct.unpack_from('4s', self.buf, offset=i+4)[0]
            chunk['content'] = self.buf[i+8:i+8+chunk['length']]
            chunk['crc32'] = hex(struct.unpack_from('>I', self.buf, offset=i+8+chunk['length'])[0])
            chunks.append(chunk)
            
            i = i + 8 + chunk['length'] + 4
        return chunks

    def parse_IHDR(self, buf):
        """
            Парсит блок данных IHDR. 
        """
        width = struct.unpack_from('>I', buf)[0]
        height = struct.unpack_from('>I', buf, offset=4)[0]
        bit_depth = struct.unpack_from('B', buf, offset=8)[0]

        try:
            color_type = COLOR_TYPES[struct.unpack_from('B', buf, offset=9)[0]]
        except KeyError:
            color_type = 'Undefined (%s)' % struct.unpack_from('B', buf, offset=9)[0]

        if struct.unpack_from('B', buf, offset=10)[0] == 0:
            compr_method = 'Deflate'
        else:
            compr_method = 'Undefined (%s)' % struct.unpack_from('B', buf, offset=10)[0]

        if struct.unpack_from('B', buf, offset=11)[0] == 0:
            filter_method = 'Adaptive Filtering'
        else:
            filter_method = 'Undefined (%s)' % struct.unpack_from('B', buf, offset=11)[0]
        
        try:
            interlace_method = INTERLACE_METHODS[struct.unpack_from('B', buf, offset=12)[0]]
        except KeyError:
            color_type = 'Undefined (%s)' % struct.unpack_from('B', buf, offset=12)[0]

        return (
            width,
            height,
            bit_depth,
            color_type,
            compr_method,
            filter_method,
            interlace_method
        )

if __name__ == '__main__':
    # import IPython; IPython.embed()
    if len(sys.argv) < 2:
        print 'Usage: python png_parser.py <path_to_png_file>'
        exit(0)

    parser = PNG_Parser(sys.argv[1])
    print parser.summary()