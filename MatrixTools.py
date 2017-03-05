import urllib

import time

import numpy
from bs4 import BeautifulSoup
from urllib.parse import urlparse


class MatrixTools():
    def __init__(self, init_site, size):
        self.start_time = time.time()
        self.size = size
        self.matrix = numpy.array([])
        self.list_links = [init_site]

    def makeMatrix(self):

        for l in self.list_links:
            if len(self.list_links) == self.size:
                break

            list_link_cur = self.getListLinks(l)
            if len(self.list_links) + len(list_link_cur) > self.size:
                k = self.size - len(list_link_cur)
                list_link_cur = list_link_cur[0:k]

            for link in list_link_cur:
                link_href = str(link.get('href'))
                self.setLinkInList(link_href, l)
        list_matrix = []
        for l in self.list_links:

            list_row = []
            links = self.purifyListSite(l, self.getListLinks(l))
            for l1 in self.list_links:
                f = False
                if l != l1:

                    for l2 in links:

                        if l2 == l1:
                            f = True
                        else:
                            f = f or False

                if f:
                    list_row.append(1)
                else:
                    list_row.append(0)



            list_matrix.append(list_row)
            list_row = []

        self.matrix = numpy.asarray(list_matrix)
        print(self.matrix)
        # print(time.time() - self.start_time, len(self.list_links), self.list_links)

    def checkLink(self, string):
        return string.startswith('/') or string.startswith('http') or string.startswith('www')

    def setLinkInList(self, link_href, init_site):
        f = True
        if len(self.list_links) < self.size:
            if self.checkLink(link_href):
                init_site = '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(init_site))
                if link_href.startswith("//"):
                    f = False

                if init_site.endswith("/"):
                    init_site = init_site[0:-1]

                if link_href.startswith("/"):
                    link_href = init_site + link_href

                if not link_href.endswith("/"):
                    link_href += "/"

                if link_href not in self.list_links and f:
                    self.list_links.append(link_href)

    def getListLinks(self, url):
        req = urllib.request.Request(
            url,
            data=None,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, '
                              'like Gecko) Chrome/35.0.1916.47 Safari/537.36 '
            }
        )
        soup = BeautifulSoup()
        try:
            f = urllib.request.urlopen(req)
            soup = BeautifulSoup(f.read(), "html.parser")
        except urllib.error.HTTPError:
            pass
        return soup.findAll('a')

    def purifyListSite(self, init_site, list_links):
        li = []
        init_site = '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(init_site))
        if init_site.endswith("/"):
            init_site = init_site[0:-1]
        for l in list_links:
            l = l.get('href')
            if l is None:
                pass
            else:
                if self.checkLink(l):
                    if l.startswith("/"):
                        l = init_site + l

                    if not l.endswith("/"):
                        l += "/"
                    li.append(l)

        return li
