#coding=utf-8
__author__ = 'dongliu'

import random


def loadfortune(datafile="res/fortune.txt"):
    fortune_list = []
    with open(datafile) as fortunefile:
        for line in fortunefile:
            line = line.strip()
            fortune_list.append(line)
    return fortune_list


_fortune_list = loadfortune()


def rand_fortune():
    idx = random.randint(0, len(_fortune_list) - 1)
    return _fortune_list[idx]

