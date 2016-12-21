#!/usr/bin/python
# -*-coding: utf-8-*-
import json
import urllib
import urllib2
import urlparse
import pdb
import os
import sys
import datetime
import random

reload(sys)
sys.setdefaultencoding('utf8')

LOCAL_PATH = './img/'


class CrawlImg(object):
    """
    爬取图片
    """

    def __init__(self):
        """
        purpose:构造函数
        """

    def download_img(self):
        """
        purpose:保存图片
        """
        # 读取单品文件
        f = open("./imgs.txt", 'r')
        for line in f.readlines():
            split_line = line.split('\t')
            item_id = split_line[0]
            img_url = split_line[1]

            print
            item_id
            print
            img_url

            file_path = self.create_file_path(img_url, item_id)

            try:
                urllib.urlretrieve(img_url, file_path)
            except Exception, e:
                print
                Exception, ":", e
                continue

        f.close()

        return (True, 'OK')

    def create_file_path(self, img_url, item_id):
        """
        purpose:创建本地保存文件路径
        input:img_url
        output:文件路径
        """
        segs = urlparse.urlparse(img_url)
        # 文件全路径
        file_path = LOCAL_PATH + str(item_id) + '.jpg'
        # 目录是否存在，不存在重新建立
        path = '/'.join(file_path.split('/')[:-1])
        isExists = os.path.exists(path)
        if not isExists:
            os.makedirs(path)

        return file_path


if __name__ == '__main__':
    crawl_img = CrawlImg()
    crawl_img.download_img()