#!/usr/bin/env python
# coding=utf-8
import urllib
import urllib2
import urlparse
import re
import os
import recognition as recog
from PIL import Image
import Queue as deque
import requests
import sys
import inspect
import argparse
from bs4 import BeautifulSoup
import proxy

LINE = inspect.currentframe()
reload(sys)  # Python2.5 初始化后会删除 sys.setdefaultencoding 这个方法，我们需要重新载入
sys.setdefaultencoding('utf-8')


class DataTeamSpider:
    def __init__(self, url=None, dest_dir=None, _list=[line for line in open('html_list.txt', 'r')]):
        self.url = url
        self.dest_dir = dest_dir
        self.list = _list
        self.url_list = deque.Queue(maxsize=100000)
        if url is not None:
            self.url_list.put(url)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36',
            'Qunar-App': 'SQxTLo6t4k5HSnsykL7nuz9jL/2FvrM9QfppVEbOhQYxIS5tR6I/w3GIq9wpZLbur3Hw7W//Ec+nFnorxB7gTlSSND1Xrbaj3zmRkWAZUaiRm+djpINDhvsYOXlFZHlrQ0BPZ+uZRIn5xnSAfPTpW1xJehqHDr1769Xs0Ly8rZM='
        }

        pass

    def getHtml(self, url=None):

        _html = None
        try:

            # page = urllib2.urlopen(self.url if url is None else url, timeout=5)
            # _html = page.read()
            _search_url = self.url if url is None else url
            _search_url = _search_url.strip('http:')
            _search_url = _search_url.strip('https:')
            _search_url = _search_url.strip('/')
            _search_url = "http://" + _search_url
            page = requests.get(_search_url, timeout=5, headers=self.headers)
            page.encoding = 'utf-8'
            _html = page.text
        except Exception, e:
            print e
            pass
        return _html

    def parseHtml(self, html, reg):
        try:
            if html is None:
                return []
            _re = re.compile(reg)
            _list = re.findall(_re, html)
            return _list
        except Exception, e:
            return None

    def parseURL(self, url, type):
        try:
            ind_s = url.rfind('="')
            if ind_s < 0:
                ind_s += len(url)
            ind_e = url.rfind(type)
            print url[ind_s + 2:ind_e + len(type)]
            return url[ind_s + 2:ind_e + len(type)] if ind_s < ind_e else url
        except Exception, e:
            pass

    def getImagePath(self, html):

        try:
            def judgeEmpty(var):
                return 'other' if var is None else var.string

            soup = BeautifulSoup(html, 'html.parser')
            first_div_model = soup.find('div', attrs={'class': 'crumb'})
            if first_div_model is None:
                return None
            for _tag in first_div_model.find_all('a'):
                print _tag.parent.name, _tag.string
                # if top_tag.string != "旅游攻略":
                #   return None

                # first_var = first_div_model.find('a', attrs={'target': '_blank'})
                # second_var = first_div_model.find('a', attrs={'target': '_parent'})
                # print 'first_var', first_var, 'second_var', second_var
                # first_var = judgeEmpty(first_var)
                # second_var = judgeEmpty(second_var)
                # return os.path.join(first_var, second_var)
        except Exception, e:
            pass

    def getImg(self, html):
        if html is None:
            return

        default_reg = r'(?:img){1}.+?="(.+?\.(jpeg|jpg|png))"?'
        x = 0
        dest_dir = self.getImagePath(html=html)
        if dest_dir is None:
            return
        dest_dir = os.path.join(self.dest_dir, dest_dir)
        for imgurl in self.parseHtml(html, default_reg):
            tmp_imgurl = (self.parseURL(imgurl[0], imgurl[1]), imgurl[1])
            del imgurl
            imgurl = tmp_imgurl

            if imgurl[0].find("http") == -1 and imgurl[0].find("com") == -1 and imgurl[0].find("cn") == -1:
                domain = self.getdomain()
                tmp_imgurl = (('/' if domain is None else domain) + imgurl[0], imgurl[1])
                del imgurl
                imgurl = tmp_imgurl
            self.create_file_path(imgurl, str(x), sub_file_path=dest_dir)
            x += 1

    def getImg(self, html, dest_dir):
        if html is None:
            return

        default_reg = r'(?:img){1}.+?="(.+?\.(jpeg|jpg|png))"?'
        x = 0
        dest_dir = os.path.join(self.dest_dir, dest_dir)
        for imgurl in self.parseHtml(html, default_reg):
            tmp_imgurl = (self.parseURL(imgurl[0], imgurl[1]), imgurl[1])
            del imgurl
            imgurl = tmp_imgurl

            if imgurl[0].find("http") == -1 and imgurl[0].find("com") == -1 and imgurl[0].find("cn") == -1:
                domain = self.getdomain()
                tmp_imgurl = (('/' if domain is None else domain) + imgurl[0], imgurl[1])
                del imgurl
                imgurl = tmp_imgurl
            self.create_file_path(imgurl, str(x), sub_file_path=dest_dir)
            x += 1

    def getdomain(self):
        for url in reversed(self.list):
            proto, rest = urllib.splittype(url)
            domain, rest = urllib.splithost(rest)
            if domain is not None:
                return domain
        return None

    def getPage(self, url=None):

        if url is None:
            if self.url is not None:
                url = self.url
            print "url　can  not be empty!", LINE.f_lineno
            return
        _cnt_try = 15
        _html = None
        while _cnt_try > 0:
            _html = self.getHtml(url)
            if _html is None or len(_html) > 1:
                break
            _cnt_try -= 1
        self.getImg(_html)
        # 防止死循环
        default_html = r'="(.+?\.(html|jsp|cn|com))"'
        fp = open("html_list.txt", 'a+')
        self.list.append(url)
        fp.writelines(url + '\n')  # 保存到文本中
        fp.close()
        self.list = [line for line in open('html_list.txt', 'r')]
        for imgurl in self.parseHtml(_html, default_html):
            tmp_imgurl = (self.parseURL(imgurl[0], imgurl[1]), imgurl[1])
            del imgurl
            imgurl = tmp_imgurl

            imgurl_find = imgurl[0] + '\n'
            if imgurl_find in self.list:
                print "已存在"
                continue
            new_imgurl = imgurl[0]
            new_imgurl = new_imgurl.lstrip('/')
            if imgurl[0].find("http") == -1 and imgurl[0].find("com") == -1 and imgurl[0].find("cn") == -1:
                domain = self.getdomain()
                new_imgurl = (('/' if domain is None else domain) + imgurl[0]).lstrip('/')
            print new_imgurl
            print "队列url个数：", self.url_list.qsize()
            if self.url_list.full():
                break
            self.url_list.put(new_imgurl)

    def create_file_path(self, img_url, item_id, sub_file_path=None):

        """
        purpose:创建本地保存文件路径
        input:img_url
        output:文件路径
        """

        file_name = ''
        rest_img_url = ''
        try_times = 5
        filesize = 1024
        while try_times > 0:
            try:
                rest_img_url = unicode(img_url[0])
                segs = urlparse.urlparse(img_url[0])
                if rest_img_url.find("http") == -1:
                    rest_img_url = 'https://' + rest_img_url.lstrip('/')
                img_name = rest_img_url.split("/")[-1]
                print "解析的名称为：", img_name
                file_path = os.path.join(self.dest_dir if sub_file_path is None else sub_file_path,
                                         img_name)
                print file_path
                if os.path.exists(file_path):  # 如果存在不再下载
                    filesize = os.path.getsize(file_path)
                    if filesize > 1024:
                        print '已经存在该文件：', file_path
                        return
                path = '/'.join(file_path.split('/')[:-1])
                isExists = os.path.exists(path)
                if not isExists:
                    os.makedirs(path)

                proxy_new = proxy.Proxy()
                _proxie = proxy_new.getProxyByTxt()
                r = requests.get(rest_img_url, proxies=_proxie, headers=self.headers, timeout=50)
                import codecs
                with codecs.open(file_path, "wb") as code:
                    code.write(r.content)
                filesize = os.path.getsize(file_path)
                if filesize < 1024:
                    print '图片为空尝试第', try_times, '次下载'
                    try_times -= 1
                    continue
                break
            except Exception, e:
                print '执行异常', file_path, rest_img_url, e
                print '尝试第', try_times, '次下载'
                try_times -= 1
                # os.remove(file_name)
                pass


def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(description='spider the web picture and recognition')
    parser.add_argument('--url', dest='url', help='input the url which need be spider',
                        default='http://www.mafengwo.cn/mdd/',
                        type=str, nargs='?')
    parser.add_argument('--dest_dir', dest='dest_dir', help='input the path-dir that you want to save ',
                        default='/media/gongxijun/fun/Ctrip_label', type=str, nargs='?')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    # http://travel.qunar.com/youji/6500530
    # http://you.ctrip.com/photos/sight/hangzhou14/r2040-63443468.html
    # http://lvyou.elong.com/5278780/tour/a9d9hc90.html
    # http://www.mafengwo.cn/mdd/
    # http://www.yododo.com/area/guide/01583038D1360041FF80808158302009
    # http://www.mafengwo.cn/mdd/ajax_photolist.php?act=getPoiPhotoList&mddid=84718&poiid=3986&page=1
    args = parse_args()
    _spilder = DataTeamSpider(args.url, args.dest_dir)
    while not _spilder.url_list.empty():
        cur_url = _spilder.url_list.get(block=False)
        print cur_url
        _spilder.getPage(url=cur_url)
