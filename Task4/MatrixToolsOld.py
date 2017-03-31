import threading
import urllib

import time

import numpy
from bs4 import BeautifulSoup
from urllib.parse import urlparse


class MatrixToolsOld():
    def __init__(self, init_site, size):
        self.d = 0.85
        self.size = size
        self.matrix = numpy.array([])
        self.matrix_list = []
        self.list_links = [init_site]
        self.links_and_size = []

    def createMatrixByRows(self, x, y):
        if x > y:
            k = x
            x = y
            y = k
        list_matrix = []
        row_number = 0
        for l in range(x, y + 1):

            list_row = []
            time.sleep(1)
            links = self.purifyListSite(self.list_links[l], self.getListLinks(self.list_links[l]))
            size = len(links)
            self.links_and_size.append([self.list_links[l], size, l])
            column_number = 0
            for l1 in self.list_links:

                f = False
                if self.list_links[l] != l1:

                    for l2 in links:

                        if l2 == l1:
                            f = True
                            break
                        else:
                            f = f or False

                if f:
                    list_row.append([l, column_number])
                    if list_row not in list_matrix:
                        list_matrix.append(list_row)
                    list_row = []
                column_number += 1
            row_number += 1

        self.matrix_list.extend(list_matrix)

    def makeMatrix(self):
        print("Собираем список ссылок...")
        start_time = time.time()
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
        print("Ok!", time.time() - start_time)

        print("Создаем разреженную матрицу...")
        start_time = time.time()
        choices_size_matrix = []
        half_size = int(self.size / 2)
        t1_size_2 = int(half_size / 2)
        t3_size_2 = int((self.size - half_size) / 2) + half_size
        choices_size_matrix.append([0, t1_size_2])
        choices_size_matrix.append([t1_size_2 + 1, half_size])
        choices_size_matrix.append([half_size + 1, t3_size_2])
        choices_size_matrix.append([t3_size_2 + 1, self.size - 1])
        t1 = threading.Thread(target=self.createMatrixByRows, name='createMatrixByRows',
                              args={choices_size_matrix[0][0], choices_size_matrix[0][1]})
        t2 = threading.Thread(target=self.createMatrixByRows, name='createMatrixByRows',
                              args={choices_size_matrix[1][0], choices_size_matrix[1][1]})
        t3 = threading.Thread(target=self.createMatrixByRows, name='createMatrixByRows',
                              args={choices_size_matrix[2][0], choices_size_matrix[2][1]})
        t4 = threading.Thread(target=self.createMatrixByRows, name='createMatrixByRows',
                              args={choices_size_matrix[3][0], choices_size_matrix[3][1]})

        t1.start()
        t2.start()
        t3.start()
        t4.start()
        t1.join()
        t2.join()
        t3.join()
        t4.join()

        self.matrix = numpy.asarray(sorted(self.matrix_list))
        self.links_and_size = sorted(self.links_and_size, key=lambda k: k[2])
        print(self.links_and_size)
        print("Ok!", time.time() - start_time)

        print("Записываем список ссылок в файл...")
        start_time = time.time()
        f = open("lists.txt", "w")
        for l in self.links_and_size:
            f.write(l[0] + "    " + str(l[1]) + " \r")
        f.close()
        print("Ok!", time.time() - start_time)

        print("Записываем матрицу в файл...")
        start_time = time.time()
        f = open("matrix.txt", "w")
        for row in self.matrix:
            for num in row:
                f.write(str(num[0]) + " " + str(num[1]))
            f.write("\r")
        f.close()
        print("Ok!", time.time() - start_time)

    def checkLink(self, string):
        return string.startswith('/') or string.startswith('http') or string.startswith('www')

    def setLinkInList(self, link_href, init_site):
        init_site.encode('utf-8')
        link_href.encode('utf-8')
        f = True
        if len(self.list_links) < self.size:
            if self.checkLink(link_href):
                init_site = '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(init_site))
                if link_href.startswith("//"):
                    f = False

                if link_href.startswith("https"):
                    link_href = link_href.replace("https", "http")

                if link_href.startswith("http://www"):
                    link_href = link_href.replace("http://www.", "http://")

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
            url[:-1],
            data=None,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, '
                              'like Gecko) Chrome/35.0.1916.47 Safari/537.36 '
            }
        )
        soup = BeautifulSoup("", "html.parser")
        try:
            f = urllib.request.urlopen(req)
            soup = BeautifulSoup(f.read(), "html.parser")
        except (urllib.error.HTTPError, urllib.error.URLError, UnicodeEncodeError):
            return []
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

                    if l.startswith("https"):
                        l = l.replace("https", "http")

                    if l.startswith("http://www"):
                        l = l.replace("http://www.", "http://")

                    if l.startswith("/"):
                        l = init_site + l

                    if not l.endswith("/"):
                        l += "/"
                    li.append(l)

        return li

    def countPagerank(self):
        print("Считываем матрицу из файла...")
        start_time = time.time()
        f = open("matrix.txt", "r")
        matrix = []
        for line in f:
            list_number_row_str = line.split(" ")
            list_number_row = []
            for l in list_number_row_str:
                try:
                    list_number_row.append(int(l))
                except ValueError:
                    pass
            matrix.append(list_number_row)
        f.close()
        matrix = numpy.asarray(matrix)
        print(matrix)
        print("Ok!", time.time() - start_time)

        print("Считываем список ссылок из файла...")
        start_time = time.time()
        f = open("lists.txt", "r")
        links_and_amount = []
        for line in f:
            line_elements = line.split("    ")
            l = [line_elements[0], int(line_elements[1])]
            links_and_amount.append(l)
        print("Ok!", time.time() - start_time)

        print("Формируем начальный список...")
        start_time = time.time()
        pr_list = []
        for l in links_and_amount:
            pr_list.append(1 / len(links_and_amount))
        print("Ok!", time.time() - start_time)

        print("Собираем входящие ссылки...")
        start_time = time.time()
        list_m = []
        for i in range(0, len(pr_list)):
            row_m = getListRowsByColumn(matrix, i)
            print(row_m)
            list_m.append(row_m)
        print("Ok!", time.time() - start_time)

        print("Считаем PageRank...")
        start_time = time.time()
        pr = []
        for j in range(0, 30):
            pr = pr_list
            for i in range(0, len(pr_list)):
                s = 0
                for l_m in list_m[i]:
                    try:
                        s += (pr[l_m] / links_and_amount[l_m][1])
                    except ZeroDivisionError:
                        pass
                pr_list[i] = (1 - self.d) / len(pr_list) + self.d * s
        print("Ok!", time.time() - start_time)

        print("Создаем соответствия PageRank и сайтов...")
        start_time = time.time()
        pr_links = []
        for l in range(0, len(links_and_amount)):
            pr_round = round(pr_list[l] * 100, 4)
            pr_links.append([links_and_amount[l], pr_round])
        print("Ok!", time.time() - start_time)

        print("Сортируем список")
        start_time = time.time()
        pr_links = sorted(pr_links, key=sort_col, reverse=True)
        print("Ok!", time.time() - start_time)

        print("Записываем PageRank сайтов в файл...")
        start_time = time.time()
        f = open("pagerank.txt", "w")
        for l in pr_links:
            f.write(str(l[1]) + " " + l[0][0] + " \r")
        f.close()
        print("Ok!", time.time() - start_time)

        print("Done!")


def getListRowsByColumn(matrix, column):
    result_list = []
    for l in matrix:
        if l[1] == column:
            result_list.append(l[0])
    return result_list


def sort_col(i):
    return i[1]