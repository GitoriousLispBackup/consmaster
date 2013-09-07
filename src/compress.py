#!/usr/bin/python3
# -*- coding: utf-8 -*-

## @package compress
# COURS   : EDF4REPA - IED - Paris 8
# PROJET  : consMaster2
# AUTEUR  : David Calmeille - 11299110@foad.iedparis8.net - L2
# FICHIER : compress.py
# CONTENU : class Compression
#                       compression maison
#                       compression LZ
#                       compression huffman
#           fonction Compression:
#                       Choisi la compression en fonction des differents ratio de compression
#           fonction decompression:
#                       decompresse en fonction du type de compression choisi.
# Description : le fichier doit etre inclus avec le serveur comme le client. Le client peut activerla compression  "On"  en changeant la valeur de COMP dans code.py  par defaut elle est a "Off".
# VERSION : 0.1
# LICENCE : GNU

import sys
from codes import *
import re
import ast


class homeCompress :
  ## home Compression
    def __init__(self, text):
          self.text = text
          self.dicompress = dicompress
          self.originalSize = sys.getsizeof(self.text)


    def replace_all(self, dic):
        for i, j in dic.items():
            self.text = self.text.replace(i, j)
        return self.text

    def compress(self) :
        self.compression = self.replace_all(self.dicompress)
        self.compresSize = sys.getsizeof(self.compression)
        self.ratio = float(self.originalSize) / self.compresSize
        self.sendHo = 'home' + self.compression


    def decompress(self) :
        self.deCompression = self.replace_all({v:k for k, v in self.dicompress.items()})
        self.deCompresSize = sys.getsizeof(self.deCompression)
        return self.deCompression


class lz :
  ## LZ Compression
    def __init__(self, text):
        self.text = text
        self.originalSize = sys.getsizeof(self.text)
        self.out = []
        self.sendLz = []
        self.word = ''

    def squeeze(self) :
        D = dict([(chr(n), n) for n in range(256)])
        code = len(D)
        for x in self.text :
            focus = self.word + x
            if focus in D :
                self.word = focus
            else :
                self.out.append(D[self.word])
                D[focus] = code
                self.word = x
                code += 1
        else :
            self.out.extend([ord(x) for x in self.word])
        self.compresSize = sys.getsizeof(self.out)
        self.ratio = float(self.originalSize) / self.compresSize
        self.sendLz = self.out
        self.sendLz.insert(0, "LZ")


    ## LZ deCompression
    def unsqueeze(self) :
        D = dict([(n, chr(n)) for n in range(256)])
        ref = len(D)
        token = self.text[0]
        self.out.append(D[token])
        for byte in self.text[1:] :
            try:
              self.word = D[byte]
            except Exception as e:
               pass
            self.out.append(self.word)
            D[ref] = D[token] + self.word[0]
            token = byte
            ref += 1
        return ''.join(self.out)

class huffman:
    def __init__(self, text):
          self.text = text
          self.prefix = {}
          self.huffannCode = []
          self.huffSend = {}
          self.getHuffSize = 0
          self.originalSize = sys.getsizeof(self.text)


    def occurrences(self) :
        o = {}
        for x in self.text : o[x] = o.get(x, 0) + 1
        return o

    def make_codes(self, node, code = '') :
        if (len(node) == 2) : self.prefix[node[1]] = code
        else :
            for i in range(2) :
                self.make_codes(node[i+1], code + str(i))

    def huffCode(self):
        F = self.occurrences()  # compute frequency table
        H = list(zip(F.values(), F.keys()))

        while H[1:] :
            H = sorted(H, key=lambda tup: tup[0])
            left = H[0]
            H.remove(left)    ## get 1st minimum
            right = H[0]
            H.remove(right)    ## get 2nd minimum
            H.append((left[0] + right[0], left, right))
        self.huffannCode = H[0]

    def huffEncode(self) :
        self.huffCode()
        self.make_codes(self.huffannCode)
        bit_string = ''.join([self.prefix[z] for z in self.text])
        code_map = dict(zip(self.prefix.values(), self.prefix.keys()))
        squeezed = []
        for b in range(0, len(bit_string), 8) :
          squeezed.append(int(bit_string[b:b+8], 2))
        else : squeezed.insert(0, len(bit_string) - b)
        format = 'original: %i, squeezed: %i, compression ratio: %2.2f'
        self.huffSend = 'huff' + str(code_map) + str(bit_string)
        self.compresSize = sys.getsizeof(self.huffSend)
        self.ratio = float(self.originalSize) / self.compresSize

    def huffDecode(self) :
        result = re.search('{(.*)}(.*)', self.text)
        code_map = ast.literal_eval("{"+ result.group(1) +"}")
        bs = result.group(2)
        code = str()
        bytes = list()

        for b in range(len(bs)) :
            code += bs[b]
            if code in code_map :
                bytes += code_map[code]
                code = str()
        self.huffdecomp = ''.join(bytes)

## decompression
class decompression:
    def __init__(self, text):
      self.text = text
      self.recomp = "Off"
      if (COMP == "On"): self.recomp = "On"

    def dataDecompression(self) :
        try :
          if(self.text[0:4] == "home"):
              new_dhc = homeCompress(self.text[4:])
              self.text = new_dhc.decompress()
              self.recomp = "On"
        except Exception as e:
            pass

        try :
          isLz = self.text[1:-1].split(', ')

          if (isLz[0] == "'LZ'") :
              lzData = [int(x) for x in isLz[1:]]
              new_lzd = lz(lzData)
              self.text = new_lzd.unsqueeze()
              self.recomp = "On"

        except Exception as e:
            pass

        try :
            if(self.text[0:4] == "huff"):
                new_hd = huffman(self.text[4:])
                new_hd.huffDecode()
                self.text = new_hd.huffdecomp
                self.recomp = "On"
        except Exception as e:
            pass

        return self.text

## Compression
class compression:
    def __init__(self, text):
          self.text = text
          self.typeComp = ''

    def dataCompression(self) :
          ratio = 0
          ##   home Compression

          new_hoc = homeCompress(self.text)
          original = new_hoc.originalSize
          new_hoc.compress()
          self.ratioHome = new_hoc.ratio
          if(ratio < new_hoc.ratio):
              ratio = new_hoc.ratio
              self.comp = new_hoc.sendHo
              self.typeComp = 'home'

          ##   LZ Compression
          new_lzc = lz(self.text)
          new_lzc.squeeze()
          self.ratioLz = new_lzc.ratio
          if(ratio < new_lzc.ratio):
              ratio = new_lzc.ratio
              self.comp =  new_lzc.sendLz
              self.typeComp = 'lz'

          ##   huffman Compression
          new_huc = huffman(self.text)
          new_huc.huffEncode()
          new_huc.huffSend
          self.ratioHuff = new_huc.ratio
          if(ratio < new_huc.ratio):
              ratio = new_huc.ratio
              self.comp = new_huc.huffSend
              self.typeComp = 'huff'

          self.prtRatio = "Original: " + str(original) + "   Maison: " + '%2.2f' % self.ratioHome + "    Lz: " + '%2.2f' % self.ratioLz + "   Huffman: " + '%2.2f' % self.ratioHuff