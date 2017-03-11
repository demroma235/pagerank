import urllib.request
from bs4 import BeautifulSoup

from MatrixTools import MatrixTools

if __name__ == '__main__':
    tools = MatrixTools("http://vk.com/", 100)
    tools.makeMatrix()
    tools.countPagerank()
