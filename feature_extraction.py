 # -*- coding: utf-8 -*-
__author__ = 'mkudinov'

import re
import sqlite3
import operator
import math

class FeatureExtraction:
    def __init__(self, features_file, numerals_file):
        self.f_features_source = features_file
        self.f_numerals_source = numerals_file
        self.numerals_regex = set([])
        self.features_regex = set([])
        self.load_feature_regexps()
        pass

    def load_feature_regexps(self):
        features_source = open(self.f_features_source)
        numerals_source = open(self.f_numerals_source)
        numerals_regex = []
        features_regex = []
        current_name = None
        for line in features_source:
            line = unicode(line, 'utf-8').strip()
            if line[0] == ':':
                current_name = line
            else:
                new_regex = re.compile(line, re.U)
                features_regex.append({'regex': new_regex, 'name': current_name})
        for line in numerals_source:
            line = unicode(line, 'utf-8').strip()
            new_regex = re.compile(line, re.U)
            numerals_regex.append(new_regex)
        self.features_regex = features_regex
        self.numerals_regex = numerals_regex
        features_source.close()
        numerals_source.close()

    def extract_features(self, candidate_list_path, index_path, binary_word_feats=False, set_entropy=False, set_pmi=False):
        sqlite_conn = sqlite3.connect(index_path)
        sqlite_cursor = sqlite_conn.cursor()
        f_candidate_list = open(candidate_list_path)
        result = {}
        for line in f_candidate_list:
            ngram = tuple(unicode(line, 'utf-8').strip().split('\t')[0].split(' '))
            sqlite_cursor.execute('SELECT counts, context_list, pmi FROM ngrams WHERE target = ?', ('_###_'.join(ngram),))
            clmns = sqlite_cursor.fetchone()
            contexts = self.deserialize_dict(clmns[1])
            if len(contexts) == 0:
                continue
            features = self.find_predefined(contexts, clmns[0], binary_word_feats)
            if set_entropy:
                features['entropy'] = self.set_entropy_feature(contexts,clmns[0])
            if set_pmi:
                features['pmi'] = clmns[2]
            result[ngram] = features
        sqlite_conn.close()
        return result

    def find_predefined(self, in_list, count, binary=False):
        out_list = {}
        out_list['__NUMERAL__'] = 0
        for word in in_list.keys():
            for regex in self.numerals_regex:
                if regex.match(word):
                    out_list['__NUMERAL__'] += in_list[word]
                    break
            for regex in self.features_regex:
                if regex['regex'].match(word):
                    if regex['name'] in in_list:
                        out_list[regex['name']] += in_list[word]
                    else:
                        out_list[regex['name']] = in_list[word]
                    break
        if binary:
            return {key: True for key, value in out_list.items() if value != 0}
        return {key: float(value) / count for key, value in out_list.items() if value != 0}

    def set_entropy_feature(self, contexts, total):
        short_list = contexts
        entropy = 0
        for word in short_list.keys():
            p = float(min(short_list[word], total)) / total
            entropy -= p * math.log(p)
        return entropy

    def merge_features(self, in_list, total):
        in_list['__NUMERAL__'] = 0
        for word in in_list.keys():
            for regex in self.numerals_regex:
                if regex.match(word):
                    in_list['__NUMERAL__'] += in_list[word]
                    in_list[word] = 0
                    break
        return {key: min(value, total) for key, value in in_list.items() if value != 0}

    def find_best(self, how_many, context_list, total, min_count):
        short_list = self.merge_features(context_list, total)
        for word in short_list.keys():
            if float(short_list[word]) / total > min_count:
                short_list[word] = math.log(float(short_list[word]) / total)
            else:
                del(short_list[word])
        sorted_list = sorted(short_list.items(), key=operator.itemgetter(1), reverse=True)
        return sorted_list if len(sorted_list) < how_many else sorted_list[0:how_many]

    def deserialize_dict(self, serialized):
        dict = {}
        if len(serialized) != 0:
            pairs = serialized.split(';')
            for pair in pairs:
                key,value = pair.split(':')
                dict[key]= int(value)
        return dict
