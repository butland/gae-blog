__author__ = 'dongliu'


class Pager(object):
    def __init__(self, total, page, pagesize):
        self.total = total
        self.page = page
        self.pagesize = pagesize

        self.totalpage = (self.total - 1) / self.pagesize + 1
        if self.totalpage < 1:
            self.totalpage = 1
        self.offset = self.pagesize * (self.page - 1)

        self.base = None
        self.show = 5

        self.begin = 1
        if self.begin < self.page - self.show:
            self.begin = self.page - self.show
        self.end = self.totalpage
        if self.end > self.page + self.show:
            self.end = self.page + self.show
        show_num = self.end - self.begin
        if show_num < self.show * 2:
            if self.begin == 1:
                self.end += self.show * 2 - show_num
                if self.end > self.totalpage:
                    self.end = self.totalpage
            elif self.end == self.totalpage:
                self.begin -= self.show * 2 - show_num
                if self.begin < 1:
                    self.begin = 1

    def setbase(self, base):
        self.base = base

    def url(self, pagenum):
        return self.base + str(pagenum)


    def hasprev(self):
        return self.page > 1

    def hasnext(self):
        return self.page < self.totalpage

    def showpages(self):
        return xrange(self.begin, self.end + 1)

    def begindot(self):
        return self.begin > 1

    def enddot(self):
        return self.end < self.totalpage