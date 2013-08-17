__author__ = 'dongliu'

# os x and linux not for sure, so more specific
computer_ua_list = ["Windows NT", "Windows XP", "Intel Mac OS X", "Macintosh", "Ubuntu", "Linux x86_64",
                    "Linux i686", "X11"]

mobile_ua_list = ["Android", "iPhone OS", "SymbianOS", "Windows Phone", "BlackBerry", "UCWEB", "webOS",
                  "UCBrowser", "Mobile Safari", "Fennec", "Opera Mobi", "IEMobile"]

pad_ua_list = ["iPad"]


class Platform(object):
    COMPUTER = 0
    MOBILE = 1
    PAD = 2
    UNKNOW = -1


def get_platform(useragent):
    if not useragent:
        return Platform.UNKNOW

    for ua in computer_ua_list:
        if ua in useragent:
            return Platform.COMPUTER

    for ua in pad_ua_list:
        if ua in useragent:
            return Platform.PAD

    # Mobile Android has "Mobile" string in the User-Agent header. Tablet Android does not.
    # Unfortunately it is not being applied by all tablet manufacturers...
    if "Android" in useragent and "Mobile" not in useragent:
        return Platform.PAD

    for ua in mobile_ua_list:
        if ua in useragent:
            return Platform.MOBILE

    return Platform.UNKNOW