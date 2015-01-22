 # -*- coding: utf-8 -*-
__author__ = 'mkudinov'

import math
import sys
import sqlite3

class ResourceFromSQL:
    def __init__(self, path, order):
        self.db = path
        self.active = True
        self.order = int(order)

    def __iter__(self):
        sqlite_conn = sqlite3.connect(self.db)
        sqlite_cursor = sqlite_conn.cursor()
        sqlite_cursor.execute("SELECT SUM(counts) FROM ngrams WHERE length = ?", (self.order,))
        total = sqlite_cursor.fetchone()
        sqlite_cursor.execute("SELECT target,counts FROM ngrams WHERE length = ?", (self.order,))
        res = sqlite_cursor.fetchall()
        for line in res:
            ngram = tuple(line[0].strip().split(u"_###_"))
            log_freq  = math.log(float(line[1]) / total[0])
            yield {'ngram': ngram, 'log_freq': float(log_freq)}
        sqlite_conn.close()

    def close(self):
        pass

class ResourceFromFile:
    def __init__(self, path):
        self.resource_file = open(path)
        self.active = True

    def __iter__(self):
        for line in self.resource_file:
            line = unicode(line, 'utf-8').strip()
            columns = line.split('\t')
            ngram, log_freq = (tuple(columns[0].split(' ')), columns[1])
            yield {'ngram': ngram, 'log_freq': float(log_freq)}

    def close(self):
        self.resource_file.close()


class NgramStat:
    def __init__(self, resource_words, resource_ngrams, resource_shorter_ngrams=None):
        self.ngram_dict = {}
        self.shorter_ngram_dict = {}
        self.word_dict = {}
        self.resource_words = resource_words
        self.resource_shorter_ngrams = resource_shorter_ngrams
        self.resource_ngrams = resource_ngrams
        self.fill_dictionaries()

    def fill_dictionaries(self):
        for word in self.resource_words:
            log_freq = word['log_freq']
            self.word_dict[word['ngram']] = log_freq
        self.resource_words.close()
        for ngram in self.resource_ngrams:
            log_freq = ngram['log_freq']
            self.ngram_dict[ngram['ngram']] = log_freq
        self.resource_ngrams.close()
        if self.resource_shorter_ngrams is not None:
            for shorter_ngram in self.resource_shorter_ngrams:
                log_freq = shorter_ngram['log_freq']
                self.shorter_ngram_dict[shorter_ngram['ngram']] = log_freq
            self.resource_shorter_ngrams.close()
        else:
            self.shorter_ngram_dict = self.word_dict

    def get_pmi(self, ngram):
        if ngram not in self.ngram_dict:
            return 0
        pmi_right = self.ngram_dict[ngram] - (self.shorter_ngram_dict[tuple(ngram[1:])] + self.word_dict[tuple(ngram[:1])])
        pmi_left = self.ngram_dict[ngram] - (self.word_dict[tuple(ngram[:1])] + self.shorter_ngram_dict[tuple(ngram[1:])])
        return min(pmi_right, pmi_left)

    def get_normalized_pmi(self, ngram):
        pmi = self.get_pmi(ngram)
        if pmi == 0:
            return 0
        return math.log(abs(pmi) * math.exp(self.ngram_dict[ngram]))

word_res = ResourceFromSQL(sys.argv[1], 1)
ngram_res = ResourceFromSQL(sys.argv[1], sys.argv[2])
if len(sys.argv) > 3:
    shorter_ngram_res = ResourceFromSQL(sys.argv[1], sys.argv[3])
else:
    shorter_ngram_res = None

stat = NgramStat(word_res, ngram_res, shorter_ngram_res)

# bigrams = open(sys.argv[2])
# rating = {}
#
# for entry in bigrams:
#     entry = unicode(entry, 'utf-8').strip()
#     columns = entry.split('\t')
#     ngram = tuple(columns[0].split(' '))
# #    print ("%s\t%s" % (' '.join(ngram), stat.get_normalized_pmi(ngram))).encode('utf-8')
#     rating[ngram] = stat.get_normalized_pmi(ngram)
#
# sorted_rating = sorted(rating.items(), key=operator.itemgetter(1), reverse=True)
#
# for entry in sorted_rating:
#     print ("%s\t%s" % (' '.join(entry[0]), entry[1])).encode('utf-8')

sql_conn = sqlite3.connect(sys.argv[1])
sql_cursor = sql_conn.cursor()
sql_cursor.execute("SELECT target FROM ngrams WHERE length = ?", (int(sys.argv[2]),))
res = sql_cursor.fetchall()
for line in res:
    sql_cursor.execute("UPDATE ngrams SET pmi=? WHERE target = ?", (stat.get_normalized_pmi(tuple(line[0].split(u'_###_'))), line[0],))
sql_conn.commit()
sql_conn.close()

