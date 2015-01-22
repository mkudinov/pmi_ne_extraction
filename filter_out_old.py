#!/usr/bin/python

import sys

f_news = open(sys.argv[1])
f_oldies = open(sys.argv[2])

dict_old = set([])

for line in f_oldies:
    name = unicode(line, 'utf-8').split('\t')[6]
    dict_old.add(name)

f_oldies.close()

for line in f_news:
    name = unicode(line, 'utf-8').split('\t')[6]
    if name not in dict_old:
        print (unicode(line, 'utf-8').strip()).encode('utf-8')
