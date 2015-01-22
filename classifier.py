 # -*- coding: utf-8 -*-
__author__ = 'mkudinov'

import sys
import pickle
import numpy as np
from sklearn import svm
from scipy.sparse import *
from sklearn.metrics import f1_score

from feature_extraction import FeatureExtraction

def get_labels_with_gazetteer(objects, gazetteer_path):
    gazetteer = []
    gzt_file = open(gazetteer_path)
    for line in gzt_file:
        ngram = tuple(unicode(line, 'utf-8').strip().split(' '))
        gazetteer.append(ngram)
    gzt_file.close()
    gazetteer = set(gazetteer)
    labels = {}
    for ngram,features in objects.iteritems():
        if ngram in gazetteer:
            labels[ngram] = True
        else:
            labels[ngram] = False
    return labels

class ClassifierPreprocess:
    def __init__(self):
        pass

    @staticmethod
    def get_feature_dict(features):
        feat_id = 0
        objects = []
        feature_dic = {}
        for ngram, feats in features.iteritems():
            objects.append(ngram)
            for feat in feats.keys():
                if feat not in feature_dic:
                    feature_dic[feat] = feat_id
                    feat_id += 1
        return objects, feature_dic

    @staticmethod
    def get_datasets(features, labels, feature_dic, test_percentage):
        sample_row_train = []
        features_row_train = []
        data_train = []
        sample_row_test = []
        features_row_test = []
        labels_train = []
        labels_test = []
        data_test = []
        iter_id = 0
        train_id = test_id = 0
        for ngram, feature_list in features.iteritems():
            if iter_id % test_percentage != 0:
                labels_train.append(labels[ngram])
                if labels[ngram] == True:
                    pass
                sample_row_train += [train_id] * len(feature_list)
                for feature,value in feature_list.iteritems():
                    if feature[0] == u'сериал':
                        pass
                    features_row_train.append(feature_dic[feature])
                    data_train.append(value)
                train_id += 1
            else:
                labels_test.append(labels[ngram])
                sample_row_test += [test_id] * len(feature_list)
                for feature,value in feature_list.iteritems():
                    features_row_test.append(feature_dic[feature])
                    data_test.append(value)
                test_id += 1
            iter_id += 1
        csr_matrix((data_train, (sample_row_train, features_row_train)),
                                     shape=(train_id, len(feature_dic)))
        return {'matrix': csr_matrix((data_train, (sample_row_train, features_row_train)),
                                     shape=(train_id, len(feature_dic))), 'labels': labels_train}, \
               {'matrix': csr_matrix((data_test, (sample_row_test, features_row_test)),
                                     shape=(test_id, len(feature_dic))), 'labels': labels_test}

    @staticmethod
    def make_feature_vector(features, feature_dic):
        result = [0] * len(feature_dic)
        for feature in features:
            result[feature_dic[feature[0]]] = feature[1]
        return np.asarray(result)

def learn_classifier(feature_table, gazetteer_path, model_path):
    classifier_learner = ClassifierLearn(10)
    labels = get_labels_with_gazetteer(feature_table, gazetteer_path)
    classifier_learner.learn(feature_table, labels)
    classifier_learner.save(model_path)

def classifier_test(dataset, gazetteer_path, model_path):
    classifier = Classifier(model_path)
    labels = get_labels_with_gazetteer(dataset, gazetteer_path)
    _, feature_dic = ClassifierPreprocess.get_feature_dict(dataset)
    for ngram in dataset.keys():
        features = dataset[ngram]
        label = labels[ngram]
        feature_vec = ClassifierPreprocess.make_feature_vector(features, feature_dic)
        prediction = classifier.classify(feature_vec)
        if prediction == True:
            pass
        if prediction != label:
            print ' '.join(ngram).encode('utf-8')
        print feature_vec
        pass
    #for

class Classifier:
    def __init__(self, path_to_model):
        self.classifier = None
        self.initialize(path_to_model)

    def initialize(self, path_to_model):
        model_file = open(path_to_model)
        self.classifier = pickle.load(model_file)
        model_file.close()

    def classify(self, object):
        return self.classifier.predict(object)

class ClassifierLearn:
    def __init__(self, test_percentage):
        self.test_percentage = test_percentage
        self.feature_dic = {}
        self.model = None

    def learn(self, features, labels):
        objects, feature_dic = ClassifierPreprocess.get_feature_dict(features)
        train_set, test_set = ClassifierPreprocess.get_datasets(features, labels, feature_dic, self.test_percentage)
        # X = train_set['matrix'].todense()
        # Y = np.asarray(train_set['labels'])
        # X_iso = manifold.Isomap(10, n_components=2).fit_transform(X)
        # plt.figure()
        # plt.title('Isomap trainset')
        # x_min, x_max = np.min(X_iso, 0), np.max(X_iso, 0)
        # X = (X_iso - x_min) / (x_max - x_min)
        # for i in range(X.shape[0]):
        #     plt.scatter(X[i, 0], X[i, 1],
        #              color=plt.cm.Set1(float(Y[i])))
        # plt.show()
        clf = svm.SVC()
        clf.fit(train_set['matrix'], train_set['labels'])
        print "Accuracy on train: ", clf.score(train_set['matrix'], train_set['labels'])
        print "Accuracy on test: ", clf.score(test_set['matrix'], test_set['labels'])
        y_pred = clf.predict(test_set['matrix'])
        print f1_score(test_set['labels'], y_pred, pos_label=True, average='macro')
        self.model = clf

    def save(self, path_to_store):
        model_file = open(path_to_store, 'w')
        pickle.dump(self.model, model_file)
        model_file.close()


mode = sys.argv[1]
model_file = sys.argv[4]
extractor = FeatureExtraction(sys.argv[5], sys.argv[6])
classifier_table = extractor.extract_features(sys.argv[2], sys.argv[3], True, True, True)
#classifier = Classifier(model_file)
if mode == "--learn":
    learn_classifier(classifier_table, sys.argv[7], model_file)
elif mode == "--test":
    classifier_test(classifier_table, sys.argv[7], model_file)
else:
    print "Wrong mode"



