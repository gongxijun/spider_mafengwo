# -*- coding: utf-8 -*-
import re
import urllib

# url that you want to download
url = "http://bbs.qyer.com/thread-810892-1.html"

# 抓取网页源码
page = urllib.urlopen(url)
html = page.read()

print "already get the source from the URL ...."

# 正则匹配
print "Starting search the picture..."

reg = r'img border="0" src="(.*?)"'
imagelist = re.findall(reg, html)

print "get it "
print "Downloading....."

# 存到本地
i = 0

for imagrul in imagelist:
    urllib.urlretrieve(imagrul, '%s.jpg' % i)
    i += 1
    print i - 1

print "workdone!"
#   urllib.urlretrieve(url,'%s.jpg' %i)
