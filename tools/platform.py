__author__ = 'dongliu'

# os x and linux not for sure, so more specific
_computer_ua_list = ["Windows NT", "Windows XP", "Intel Mac OS X", "Macintosh", "Ubuntu", "Linux x86_64",
                     "Linux i686", "X11"]

_mobile_ua_list = ["Android", "iPhone OS", "SymbianOS", "Windows Phone", "BlackBerry", "UCWEB", "webOS",
                   "UCBrowser", "Mobile Safari", "Fennec", "Opera Mobi", "IEMobile"]

_pad_ua_list = ["iPad"]

COMPUTER = 0
PHONE = 1
PAD = 2
UNKNOW = -1


def get_platform(useragent):
    if not useragent:
        return UNKNOW

    for ua in _computer_ua_list:
        if ua in useragent:
            return COMPUTER

    # pad is prior to phone
    for ua in _pad_ua_list:
        if ua in useragent:
            return PAD

    # Mobile Android has "Mobile" string in the User-Agent header. Tablet Android does not.
    # Unfortunately it is not being applied by all tablet manufacturers...
    if "Android" in useragent and "Mobile" not in useragent:
        return PAD

    for ua in _mobile_ua_list:
        if ua in useragent:
            return PHONE

    return UNKNOW