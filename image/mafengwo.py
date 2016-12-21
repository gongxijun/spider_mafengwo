#!/usr/bin/env python
# -*-coding:utf-8-*-
import urllib2
import urllib
from  bs4 import BeautifulSoup
import sys
import os
import random
import requests
import proxy
import inspect
import codecs
import json
import spider_image as spider
import argparse
from collections import OrderedDict
import threading, os, time

LINE = inspect.currentframe()
status_code_not_found = 404  # 没有找到相关网页
status_code_forbid = 403  # 禁止访问
MAX_PAGE = 60


class Mafengwo:
    def __init__(self):
        self.root_url = "http://www.mafengwo.cn/travel-scenic-spot/mafengwo"  # 地区
        self.gonglve_url = "http://www.mafengwo.cn/jd"  # 景点
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36',
            'Qunar-App': 'SQxTLo6t4k5HSnsykL7nuz9jL/2FvrM9QfppVEbOhQYxIS5tR6I/w3GIq9wpZLbur3Hw7W//Ec+nFnorxB7gTlSSND1Xrbaj3zmRkWAZUaiRm+djpINDhvsYOXlFZHlrQ0BPZ+uZRIn5xnSAfPTpW1xJehqHDr1769Xs0Ly8rZM='}
        pass

    def entry(self):
        """
        需要扫描的html的入口
        :param url:
        :return: 使用代理返回wrapper部分代码
        """
        proxy_new = proxy.Proxy()
        _proxie = proxy_new.getProxyByTxt()
        _html = None
        # 读取city_info信息
        status_ma = 26679
        try_times = 10
        while True:
            try:
                if try_times < 1:
                    try_times = 10
                    print '放弃 ', status_ma, ' 字段进入下一次字段更新'
                    status_ma += 1
                url = os.path.join(self.root_url, str(status_ma) + ".html")
                res = requests.get(url=url, proxies=_proxie, timeout=5, headers=self.headers)
                print res.status_code, status_ma, url
                if res.status_code == status_code_not_found:
                    status_ma += 1
                    try_times = 10
                    continue
                if res.status_code == status_code_forbid:
                    continue
                city_info = self.get_travel_scenic_spot(html=res.text)
                if city_info is None:
                    print "出现问题的url：", url, "出现问题的原因：", "没有获取到city_info的相关信息"
                    status_ma += 1
                    try_times = 10
                    continue
                print 'city_info:', city_info
                fp = codecs.open("city_info", 'a+', encoding='utf-8')
                fp.writelines(city_info)  # 保存到文本中
                fp.writelines("\t")
                fp.writelines(str(status_ma))
                fp.writelines("\n")
                fp.close()
                status_ma += 1
                try_times = 10
            except Exception, e:
                print "出现问题 line", LINE.f_lineno, "错误类型", e
                print '倒计时次数：', try_times
                try_times -= 1
                _proxie = proxy_new.getProxyByTxt()
                pass

    def get_travel_scenic_spot(self, html):
        """

        :param html:
        :return:
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            first_div_model = soup.find('div', attrs={'class': 'wrapper'})
            sub_path = None
            for top_domain in first_div_model.find_all('span', attrs={'class': 'hd'}):
                tag_a = top_domain.find('a')
                sub_path = tag_a.text if sub_path is None else os.path.join(sub_path, tag_a.text)
            return sub_path
        except Exception, e:
            print "出现问题 line", LINE.f_lineno, "错误类型", e
            return None

    def get_image_post(self, iMddid, iPage, iTagId, default_url="http://www.mafengwo.cn/ajax/router.php"):
        """
        返回页面
        :param iMddid:
        :param iPage:
        :param iTagId:
        :param default_url:
        :return:
        """
        try_times = 5
        while try_times > 0:
            try:
                proxy_new = proxy.Proxy()
                _proxie = proxy_new.getProxyByTxt()
                data = {'sAct': 'KMdd_StructWebAjax|GetPoisByTag',
                        'iMddid': str(iMddid).strip('\n'),
                        'iTagId': str(iTagId).strip('\n'),
                        'iPage': str(iPage).strip('\n')}
                context = requests.post(default_url, proxies=_proxie, timeout=5, data=data, headers=self.headers)
                return context.text
            except Exception, e:
                print "出现问题 line", LINE.f_lineno, "错误类型", e
                print '倒计时次数:', try_times
                try_times -= 1
                pass

    def getPoiPhottoList(self, mddid, poiid, page,
                         default_url="http://www.mafengwo.cn/mdd/ajax_photolist.php"):
        """

        :param mddid:
        :param poiid:
        :return:
        """
        try_times = 5
        while try_times > 0:
            try:
                proxy_new = proxy.Proxy()
                _proxie = proxy_new.getProxyByTxt()
                data = {'act': 'getPoiPhotoList',
                        'mddid': str(mddid).strip('\n'),
                        'poiid': str(poiid).strip('\n'),
                        'page': str(page).strip('\n')}
                context = requests.get(default_url, proxies=_proxie, params=data, timeout=5, headers=self.headers)
                context.encoding = 'utf-8'
                return context.text
            except Exception, e:
                print "出现问题 line", LINE.f_lineno, "错误类型", e
                print '倒计时次数：', try_times
                try_times -= 1
                pass

    def get_poi_list(self, iMddid, html):
        """
        获取总共页码
        :param html:
        :return:
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            top_domain = soup.find_all('a', attrs={'target': '_blank'})
            if top_domain is None:
                return
            for tag_a in top_domain:
                area_name = tag_a['title']
                poi_href = tag_a['href']
                if poi_href is not None:
                    poi_href = poi_href.split('/')[-1].split('.')[0]
                info = str(iMddid).strip('\n') + '\t' + poi_href + '\t' + area_name + '\n'
                print 'info:', info
                fp = codecs.open("poi_info", 'a+', encoding='utf-8')
                fp.writelines(info)  # 保存到文本中
                fp.close()
        except Exception, e:
            print "出现问题 line", LINE.f_lineno, "错误类型", e
            pass

    def get_total_page(self, html):
        """
        解析poi_html
        :param html:
        :return: 将数据写入到文件中 poi_list: 文件格式 Mddid poi 名称
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            top_domain = soup.find('span', attrs={'class': 'count'})
            if top_domain is None:
                return 1
            tag_span = top_domain.find_all('span')
            return int(tag_span[0].text)
        except Exception, e:
            print "出现问题 line", LINE.f_lineno, "错误类型", e
            return 1

    def get_poi(self, html, iMddid):
        data = self.get_image_post(iMddid=iMddid, iPage=1, iTagId=0)
        _json = json.loads(data, encoding='utf-8')
        ddata = _json['data']
        for _page in range(1, self.get_total_page(html=ddata['page']) + 1):
            data = self.get_image_post(iMddid=iMddid, iPage=_page, iTagId=0)
            _json = json.loads(data, encoding='utf-8')
            tmp_data = _json['data']
            html_list = tmp_data['list']
            # 解析代码
            # print html_list
            self.get_poi_list(iMddid=iMddid, html=html_list)
        return None

    def get_gonglve(self):
        """

        :return:
        """
        proxy_new = proxy.Proxy()
        _proxie = proxy_new.getProxyByTxt()
        _html = None
        # 读取city_info信息
        for lines in codecs.open('city_info', 'r', encoding='utf-8'):
            status_ma = lines.split('\t')[-1]
            try_times = 5
            while try_times > 0:
                try:
                    url = os.path.join(os.path.join(self.gonglve_url, unicode(str(status_ma).strip('\n'))),
                                       "gonglve.html")
                    res = requests.get(url=url, proxies=_proxie, timeout=5, headers=self.headers)
                    print res.status_code, status_ma, url
                    if res.status_code == status_code_not_found:
                        status_ma += 1
                        continue
                    if res.status_code == status_code_forbid:
                        continue
                    self.get_poi(html=res.text, iMddid=status_ma)
                    break
                except Exception, e:
                    print "出现问题 line", LINE.f_lineno, "错误类型", e
                    print '尝试倒计次数：', try_times
                    try_times -= 1
                    pass

    def get_proxy(self, poi_file_path='./poi_info', city_info_file_path='./city_info'):
        """
        :param poi_file_path:
        :param city_info_file_path:
        :return:
        """
        city_info = dict()
        poi_city = dict()  # poiid 对应的mddid
        poi_name = dict()  # poiid 对应的景点名
        for _city in codecs.open('city_info', 'r', encoding='utf-8'):
            _city_info = _city.split('\t')
            city_info[_city_info[1].strip('\n')] = _city_info[0].strip('\n')
        for _poi_info in codecs.open('poi_info_step_1', 'r', encoding='utf-8'):
            tmp_poi_info = _poi_info.split('\t')
            poi_city[tmp_poi_info[1].strip('\n')] = tmp_poi_info[0].strip('\n')
            poi_name[tmp_poi_info[1].strip('\n')] = tmp_poi_info[2].strip('\n')
        return city_info, poi_city, poi_name


def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(description='spider the web picture and recognition')
    parser.add_argument('--url', dest='url', help='input the url which need be spider',
                        default='http://www.mafengwo.cn/mdd/',
                        type=str, nargs='?')
    parser.add_argument('--stride', dest='stride', help='input the num that you want the size ',
                        default=5, type=int, nargs='?')
    parser.add_argument('--dest_dir', dest='dest_dir', help='input the path-dir that you want to save ',
                        default='/media/gongxijun/fun/new_Ctrip_label', type=str, nargs='?')
    args = parser.parse_args()
    return args


def thread_main(start, stride, dest_dir):
    _Mafengwo = Mafengwo()
    _spider = spider.DataTeamSpider(dest_dir=dest_dir)
    # _Mafengwo.get_gonglve()
    # _Mafengwo.entry()
    city_info, poi_city, poi_name = _Mafengwo.get_proxy()
    # item_poi_city = OrderedDict(sorted(poi_city.items(), key=lambda t: t[0], reverse=True))
    for _poi in poi_city:
        if start > 0:
            start -= 1
            continue
        start = stride
        _page = 1
        while _page < MAX_PAGE:
            mddid = poi_city[_poi]
            text = _Mafengwo.getPoiPhottoList(mddid=mddid, poiid=_poi, page=_page)
            print city_info[mddid]
            sub_path = os.path.join(city_info[mddid], poi_name[_poi])
            _spider.getImg(text, sub_path)
            if len(text) < 10:
                break
            _page += 1


def total_main():
    args = parse_args()
    _index = 0
    _thread_Image = [0] * args.stride
    for _index in range(args.stride):
        _thread_Image[_index] = threading.Thread(target=thread_main, args=(_index, args.stride, args.dest_dir))
        _thread_Image[_index].start()
        _index += 1
        time.sleep(0.3)


if __name__ == '__main__':
    #args = parse_args()
    #_Mafengwo = Mafengwo()
    # _Mafengwo.get_gonglve()
    #_Mafengwo.entry()
    total_main()
