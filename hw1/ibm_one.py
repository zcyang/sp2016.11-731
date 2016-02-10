#/usr/bin/env python

import pdb
import argparse

from collections import defaultdict

def get_vocab_dict(bitext):
    f_dict = defaultdict(int)
    e_dict = defaultdict(int)
    fe_prob = defaultdict(float)
    for (f, e) in bitext:
        for f_i in set(f):
            f_dict[f_i] = 1
            for e_j in set(e):
                fe_prob[(f_i, e_j)] = 1.0
        for e_j in set(e):
            e_dict[e_j] = 1
    # initialize dictionary
    return f_dict, e_dict, fe_prob

def m_step(bitext, fe_prob, f_dict, e_dict):
    align_list = []
    for (f, e) in bitext:
        align_dict = defaultdict(float)
        for e_j in e:
            sum_prob = 0
            for f_i in f:
                sum_prob += fe_prob[(f_i, e_j)]
            for f_i in f:
                align_dict[(f_i, e_j)] = fe_prob[(f_i, e_j)] / sum_prob
        align_list.append(align_dict)
    return align_list

def e_step(align_list, f_dict, e_dict):
    fe_prob = defaultdict(float)
    sum_prob = defaultdict(float)
    for f_e in align_list:
        for (f_i, e_j) in f_e.keys():
            fe_prob[(f_i, e_j)] += f_e[(f_i, e_j)]
            sum_prob[f_i] += f_e[(f_i, e_j)]
    # normalize
    for (f_i, e_j) in fe_prob.keys():
        fe_prob[(f_i, e_j)] /= sum_prob[f_i]
    return fe_prob

def output_alignment(align_dict, bitext, file_name, threshold):
    f_output = open(file_name, 'w')
    for ((f, e), a) in zip(bitext, align_dict):
        output_line = ''
        for j, e_j in enumerate(e):
            max_prob = 0.
            max_idx = 0.
            for i, f_i in enumerate(f):
                if a[(f_i, e_j)] > max_prob:
                    max_idx = i
                    max_prob = a[(f_i, e_j)]
            if max_prob > threshold:
                output_line += str(max_idx) + '-' + str(j) + ' '
        f_output.write(output_line + '\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_file', default='data/dev-test-train.de-en')
    parser.add_argument('--max_iter', default=10)
    parser.add_argument('--output_file', default='output.txt')
    parser.add_argument('--threshold', default=0.)
    args = parser.parse_args()

    bitext = [[sentence.strip().split() for sentence in pair.split(' ||| ')] for
              pair in open(args.data_file)]
    print 'finished loading data'
    f_dict, e_dict, fe_prob = get_vocab_dict(bitext)
    print 'finished building dict'
    for i in range(args.max_iter):
        align_list = m_step(bitext, fe_prob, f_dict, e_dict)
        output_alignment(align_list, bitext, args.output_file + '_' + str(i),
                         args.threshold)
        fe_prob = e_step(align_list, f_dict, e_dict)
        print 'iteation ' + str(i)
