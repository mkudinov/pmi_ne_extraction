 # -*- coding: utf-8 -*-
__author__ = 'mkudinov'

import operator
import sys

ngrams_2 = {}
ngrams_3 = {}
ngrams_4 = {}
ngrams_5 = {}
ngrams_6 = {}

ngrams = [ngrams_2, ngrams_3, ngrams_4, ngrams_5, ngrams_6]

input_file = open(sys.argv[1])

for line in input_file:
    line = unicode(line, 'utf-8').strip()
    columns = line.split('\t')
    ngram = tuple(columns[0].split(' '))
    ngram_len = len(ngram) - 2
    ngrams[ngram_len][ngram] = float(columns[1])
    if float(columns[1]) < -9.0:
        break
input_file.close()

rating = {}

for ngram_len in range(5, 2, -1):
    ngrams_n = ngrams[ngram_len - 2]
    ngrams_nm1 = ngrams[ngram_len - 3]
    for ngram in ngrams_n.keys():
        postfix = ngram[1:]
        if postfix in ngrams_nm1 and ngrams_nm1[postfix] < ngrams_n[ngram]:
            ngrams_nm1.pop(postfix)
        rating[' '.join(ngram)] = ngrams_n[ngram]

for ngram in ngrams[0].keys():
    rating[' '.join(ngram)] = ngrams[0][ngram]

sorted_rating = sorted(rating.items(), key=operator.itemgetter(1), reverse=True)

for entry in sorted_rating:
    print ("%s\t%s" % (entry[0], entry[1])).encode('utf-8')