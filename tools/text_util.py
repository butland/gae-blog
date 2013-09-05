__author__ = 'dongliu'


def subStr(str, length):
    #str must be unicode
    if str is None:
        return None
    if len(str) * 2 < length:
        return str
    pos = -1
    curlen = 0
    low = 0x4E00
    high = 0x9FA5
    for ch in str:
        if low <= ord(ch) <= high:
            curlen += 2
        else:
            curlen += 1
        pos += 1
        if curlen > length:
            break
    if pos >= len(str):
        return str
    if pos > 2:
        pos -= 2
    return str[0:pos] + '...'