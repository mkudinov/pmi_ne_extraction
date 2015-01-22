 # -*- coding: utf-8 -*-
__author__ = 'mkudinov'

import sys
import copy
import sqlite3

class NgramStorage:
    def __init__ (self, path_to_storage, max_internal_storage):
        self.counts = {}
        self.max_internal_storage = max_internal_storage
        self.contexts1 = {}
        self.contexts2 = {}
        self.current_context = self.contexts1
        self.db = path_to_storage
        sqlite_conn = sqlite3.connect(self.db)
        sqlite_cursor = sqlite_conn.cursor()
        sqlite_cursor.execute('SELECT target, context_list, counts FROM ngrams')
        res = sqlite_cursor.fetchall()
        if res is None:
            return
        for line in res:
            ngram = tuple(line[0].strip().split("_###_"))
            self.current_context[ngram] = self.deserialize_dict(line[1])
            self.counts[ngram] = line[2]
        print "Initialized"

    def insert(self, key, context_dic):
        if key not in self.current_context:
            self.current_context[key] = {}
        for elem, count in context_dic.iteritems():
            if elem in self.current_context[key]:
                self.current_context[key][elem] += count
            else:
                self.current_context[key][elem] = count

        # if len(self.current_context) > self.max_internal_storage:
        #     self.make_dump(False)

    # def wait_for_mutex(self, list_to_wait):
    #     print 'wait'
    #     while len(list_to_wait) > 0:
    #         pass
    #     print 'ok'

    # def __dump(self, list_to_dump):
    #     sqlite_conn = sqlite3.connect(self.db)
    #     sqlite_cursor = sqlite_conn.cursor()
    #     a = 0
    #     for key,contexts in list_to_dump.iteritems():
    #         sqlite_cursor.execute('SELECT context_list, counts FROM ngrams WHERE target=?', ('_'.join(key),))
    #         res = sqlite_cursor.fetchone()
    #         temp_dict = {}
    #         counts = 0
    #         if res is None:
    #             sqlite_cursor.execute("INSERT INTO ngrams VALUES (?,0,'',0)", ('_'.join(key),))
    #         else:
    #             temp_dict = self.deserialize_dict(res[0])
    #             counts = res[1]
    #         for word,count in contexts.iteritems():
    #             if word in temp_dict:
    #                 temp_dict[word] += count
    #             else:
    #                 temp_dict[word] = count
    #         sqlite_conn.execute('UPDATE ngrams SET context_list = ?, counts = ? WHERE target=?', (self.serialize(temp_dict), counts + self.counts[key], '_'.join(key),))
    #         self.counts[key] = 0
    #         a+=1
    #         print a
    #     sqlite_conn.commit()
    #     sqlite_conn.close()
    #     list_to_dump.clear()

    def simple_dump(self, list_to_dump):
        sqlite_conn = sqlite3.connect(self.db)
        sqlite_cursor = sqlite_conn.cursor()
        for key,contexts in list_to_dump.iteritems():
            temp_dict = {}
            for word,count in contexts.iteritems():
                    temp_dict[word] = count
            sqlite_cursor.execute('INSERT OR REPLACE INTO ngrams VALUES (?,?,?,?,?,?)', ('_###_'.join(key), self.counts[key], self.serialize(temp_dict), len(key), 0, 0))
        sqlite_conn.commit()
        sqlite_conn.close()
        list_to_dump.clear()

    def serialize(self, dict):
        res = []
        for key, value in dict.iteritems():
            res.append(':'.join((key,str(value),)))
        return ';'.join(res)

    def deserialize_dict(self, serialized):
        dict = {}
        if len(serialized) != 0:
            pairs = serialized.split(';')
            for pair in pairs:
                key,value = pair.split(':')
                dict[key]= int(value)
        return dict

    # def start_dump_to_disk(self, list_to_dump, join):
    #     thread = Thread(target = self.__dump, args=(list_to_dump, ))
    #     thread.start()
    #     if join:
    #         thread.join()

    def select(self, key):
        #TODO
        pass

    # def make_dump(self, isFinal):
    #     if self.current_context is self.contexts1:
    #         if len(self.contexts2) != 0:
    #             self.wait_for_mutex(self.contexts2)
    #         self.current_context = self.contexts2
    #         self.start_dump_to_disk(self.contexts1, isFinal)
    #     else:
    #         if len(self.contexts1) != 0:
    #             self.wait_for_mutex(self.contexts1)
    #         self.current_context = self.contexts1
    #         self.start_dump_to_disk(self.contexts2, isFinal)


class Indexer:
    def __init__(self, storage_path):
        #self.counts = {}
        self.storage = NgramStorage(storage_path, 10000)

    def process_file(self, path):
        source = open(path,'r')
        for line in source:
            line = unicode(line, 'utf-8').strip()
            count, query = line.split('\t')
            words = query.split(' ')
            for order_i in range(6):
                order = order_i + 1
                self.extract_ngrams(words, order=order, coefficient=int(count))
        source.close()
        if len(self.storage.current_context) != 0:
            self.storage.simple_dump(self.storage.current_context)

        # for ngram in self.counts:
        #     print ("%s\t%s" % (' '.join(ngram), math.log(self.counts[ngram]) - math.log(self.total))).encode('utf-8')

    def extract_ngrams(self, words, order=2, coefficient=1):
        if len(words) < order:
            return

        temp_dict = {}

        for word in words:
            if word in temp_dict:
                temp_dict[word] += coefficient
            else:
                temp_dict[word] = coefficient

        for i in range(len(words) - order + 1):
            ngram = tuple(words[i:i+order])
            temp_dict2 =  copy.deepcopy(temp_dict)
            for gram in ngram:
                temp_dict2[gram] -= coefficient
                if temp_dict2[gram] == 0:
                    del temp_dict2[gram]

            if ngram in self.storage.counts:
                self.storage.counts[ngram] += coefficient

            else:
                self.storage.counts[ngram] = coefficient

            self.storage.insert(ngram, temp_dict2)

 #       self.storage.total += (len(words) - order + 1) * coefficient

def drop_database(path):
    sqlite_conn = sqlite3.connect(path)
    sqlite_cursor = sqlite_conn.cursor()
    sqlite_cursor.execute("DROP TABLE IF EXISTS ngrams")
    sqlite_cursor.execute("CREATE TABLE ngrams (target PRIMARY KEY, counts, context_list, length, pmi, inspection_status)")
    sqlite_cursor.execute("CREATE INDEX ngram_order ON ngrams (length)")
    sqlite_conn.commit()
    sqlite_conn.close()

path_to_db = sys.argv[1]
path_to_queries = sys.argv[2]
if len(sys.argv) > 3 and sys.argv[3] == "--drop-db":
    drop_database(path_to_db)

indexer = Indexer(path_to_db)
indexer.process_file(path_to_queries)

#indexer.process_file('test')