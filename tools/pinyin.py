#coding=utf-8
__author__ = 'dongliu'

# SIMPLE for chinese characters to pinyin.

_pinyin_dict = {}


def loadpinyindata(datafile="res/pinyin.data"):
    with open(datafile) as pinyin_file:
        for line in pinyin_file:
            line = line.strip()
            items = line.split(' ')
            if len(items) != 2:
                continue
            ch = unichr(int(items[0], 16))

            pinyin = items[1]
            idx = pinyin.find(',')
            if idx > 0:
                pinyin = pinyin[0:idx]
            pinyin = pinyin[:-1]
            if pinyin == "none":
                continue
            _pinyin_dict[ch] = pinyin.decode('utf-8')

loadpinyindata()


def getpinyin(str):
    if type(str) != type(u''):
        raise Exception("Must be unicode type.")
    if str is None or len(str) == 0:
        return str
    pinyins = []
    for ch in str:
        if ch in _pinyin_dict:
            pinyins.append(_pinyin_dict[ch])
        else:
            pinyins.append(ch)
    return u''.join(pinyins)