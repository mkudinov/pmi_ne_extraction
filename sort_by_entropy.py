 # -*- coding: utf-8 -*-
__author__ = 'mkudinov'

import sqlite3
from feature_extraction import FeatureExtraction
import math
import operator

extractor = FeatureExtraction("feature_words", "feature_numerals")
sqlite_conn = sqlite3.connect("tvindex.db")
sqlite_cursor = sqlite_conn.cursor()
f_candidate_list = open("cleaned")
entropies = {}
context_list = {}
for line in f_candidate_list:
    if  unicode(line, 'utf-8').strip().split('\t')[0] == u'один портал в город жителей':
        pass
    ngram = tuple(unicode(line, 'utf-8').strip().split('\t')[0].split(' '))
    sqlite_cursor.execute('SELECT counts, context_list FROM ngrams WHERE target = ?', ('_###_'.join(ngram),))
    clmns = sqlite_cursor.fetchone()
    total = int(clmns[0])
    contexts = extractor.deserialize_dict(clmns[1])
    if len(contexts) == 0:
        continue
#    short_list = extractor.merge_features(contexts)
    short_list = contexts
    entropy = 0
    for word in short_list.keys():
            p = float(min(short_list[word], total)) / total
            entropy -= p * math.log(p)
    if entropy != 0:
        entropies[ngram] = entropy
    context_list[ngram] = contexts
sqlite_conn.close()

# entropies = {}
#
# for ngram, distribution in result.iteritems():
#     entropy = 0
#     for word_prob in distribution.values():
#         entropy += -math.log(word_prob)
#     entropy /= len(distribution)
#     entropies[' '.join(ngram)] = entropy

sorted_rating = sorted(entropies.items(), key=operator.itemgetter(1))
for entry in sorted_rating:
    if u'смотреть' in context_list[entry[0]] and u'серия' not in entry[0]:
        print ("%s\t%s" % (' '.join(entry[0]), entry[1])).encode('utf-8')