#!/usr/bin/python
__author__ = 'mkudinov'

import sys
import math

class QueryNgramsCalculator:
    def __init__(self):
        self.counts = {}
        self.total = 0

    def process_file(self, path, ngram_order = 2):
        source = open(path,'r')
        for line in source:
            line = unicode(line, 'utf-8').strip()
            count, query = line.split('\t')
            self.extract_ngrams(query=query, order=ngram_order, coefficient=int(count))
        source.close()
        for ngram in self.counts:
            print ("%s\t%s" % (' '.join(ngram), math.log(self.counts[ngram]) - math.log(self.total))).encode('utf-8')

    def extract_ngrams(self, query, order=2, coefficient=1):
        words = query.split(' ')
        if len(words) < order:
            return
        for i in range(len(words) - order + 1):
            ngram = tuple(words[i:i+order])
            if ngram in self.counts:
                self.counts[ngram] += coefficient
            else:
                self.counts[ngram] = coefficient
        self.total += (len(words) - order + 1) * coefficient


order = int(sys.argv[2])
path = sys.argv[1]
processor = QueryNgramsCalculator()
processor.process_file(path, ngram_order=order)
