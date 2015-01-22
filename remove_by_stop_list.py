__author__ = 'mkudinov'

import sys, re

class ListFilterByStopWords:
    def __init__(self, numerals_path, stopwords_path):
        self.f_numerals = open(numerals_path)
        self.f_stopwords = open(stopwords_path)
        self.regex = []
        self.create_re_list()

    def create_re_list(self):
        for line in self.f_stopwords:
            line = unicode(line, 'utf-8').strip()
            self.regex.append(re.compile(line, re.UNICODE))
        for line in self.f_numerals:
            line = unicode(line, 'utf-8').strip()
            self.regex.append(re.compile(line))
        self.f_numerals.close()
        self.f_stopwords.close()

    def filter_list(self, list_path):
        result = []
        f_list = open(list_path)
        for line in f_list:
            line = unicode(line, 'utf-8').strip()
            line = line.split('\t')[0]
            normalnyi = True
            for regex in self.regex:
                if regex.search(line) is not None:
                    normalnyi = False
                    break
            if normalnyi:
                result.append(line)
        return result

remover = ListFilterByStopWords(sys.argv[1], sys.argv[2])
list = remover.filter_list(sys.argv[3])

for line in list:
    print ("RU\tRU\tTITLE\t%s\t%s\t%s\t%s\tLOG_CHECK\tNEW" % (line, line, line.title(), line)).encode('utf-8')