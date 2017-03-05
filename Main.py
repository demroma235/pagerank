import urllib.request
from bs4 import BeautifulSoup

from MatrixTools import MatrixTools

if __name__ == '__main__':
    tools = MatrixTools("http://www.kpfu.ru/", 10)
    tools.makeMatrix()
