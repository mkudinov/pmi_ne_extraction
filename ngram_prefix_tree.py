 # -*- coding: utf-8 -*-
__author__ = 'mkudinov'

import copy
import operator
import sys
import sqlite3

class NgramPrefixNode:
    def __init__(self, parent = None, word=None, pmi=-10e3):
        self.word = word
        self.parent = parent
        self.children = {}
        self.pmi = pmi

    def get_child(self, word):
        if word in self.children:
            return self.children[word]
        else:
            return None

    def traverse(self, ngram_so_far, store):
        if self.parent is not None and self.pmi < self.parent.pmi:
            return False
        if len(self.children) == 0:
            ngram_so_far.append(self.word)
            store[' '.join(ngram_so_far)] = self.pmi
            return True
        success_branch = False
        for child in self.children.keys():
            new_ngram = copy.deepcopy(ngram_so_far)
            if self.word is not None:
                new_ngram.append(self.word)
            success_branch = self.children[child].traverse(new_ngram, store) or success_branch
        if not success_branch:
            ngram_so_far.append(self.word)
            store[' '.join(ngram_so_far)] = self.pmi
        return True

class NgramPrefixTree:
    def __init__(self):
        self.root = NgramPrefixNode()

    def add(self, ngram, pmi=-10e3):
        parent = self.find(ngram[:-1])
        if not parent.children.has_key(ngram[-1]):
            new_node = NgramPrefixNode(parent, ngram[-1], pmi)
            parent.children[ngram[-1]] = new_node

    def find(self, ngram):
        current_node = self.root
        if ngram == (None,):
            return current_node
        for word in ngram:
            current_node = current_node.get_child(word)
            if current_node is None:
                raise("No prefix for non-root ngram")
        return current_node

def load_initial(bigrams, prefix_tree):
    for bigram in bigrams.keys():
#        if bigram[0] == u'битва':
        prefix_tree.add((None, bigram[0]))
        prefix_tree.add(bigram, bigrams[bigram])

# bigram_file = open(sys.argv[1])
bigram_list = {}
sqlite_conn = sqlite3.connect(sys.argv[1])
sqlite_cursor = sqlite_conn.cursor()
sqlite_cursor.execute("SELECT target,pmi FROM ngrams WHERE length = 2")
res = sqlite_cursor.fetchall()
for line in res:
    ngram = tuple(line[0].strip().split(u"_###_"))
    bigram_list[ngram] = float(line[1])


# for line in bigram_file:
#     line = unicode(line, 'utf-8').strip()
#     columns = line.split('\t')
#     bigram_list[tuple(columns[0].split(' '))] = float(columns[1])
#
tree = NgramPrefixTree()
load_initial(bigram_list, tree)
#
sqlite_cursor.execute("SELECT target,pmi FROM ngrams WHERE length > 2")
res = sqlite_cursor.fetchall()
for line in res:
    ngram = tuple(line[0].strip().split(u"_###_"))
    tree.add(ngram, float(line[1]))

# trigram_file = open(sys.argv[2])
# for line in trigram_file:
#     line = unicode(line, 'utf-8').strip()
#     columns = line.split('\t')
#     nnn = tuple(columns[0].split(' '))
#     tree.add(nnn, float(columns[1]))
#
# quatrgram_file = open(sys.argv[3])
# for line in quatrgram_file:
#     line = unicode(line, 'utf-8').strip()
#     columns = line.split('\t')
#     tree.add(tuple(columns[0].split(' ')), float(columns[1]))
#
# if len(sys.argv) > 4:
#     quintrgram_file = open(sys.argv[4])
#     for line in quintrgram_file:
#         line = unicode(line, 'utf-8').strip()
#         columns = line.split('\t')
#         tree.add(tuple(columns[0].split(' ')), float(columns[1]))

rating = {}

tree.root.traverse([], rating)
sorted_rating = sorted(rating.items(), key=operator.itemgetter(1), reverse=True)

for entry in sorted_rating:
    print ("%s\t%s" % (entry[0], entry[1])).encode('utf-8')

