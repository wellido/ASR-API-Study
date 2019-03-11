#/usr/bin/env python
# coding=utf8
 
import http.client
import hashlib
import urllib.request, urllib.parse, urllib.error
import random
from base64 import b64decode, b64encode
from urllib.request import urlopen
from urllib.request import Request
from urllib.error import URLError
from urllib.parse import urlencode
import zlib

appid = '20190311000276027' #你的appid
secretKey = 'gmKqkKmSJqJztnG0Dz_L' #你的密钥

 
httpClient = None
myurl = '/api/trans/vip/translate'
# q = '苹果'
# fromLang = 'zh'
# toLang = 'en'


# 输入
q = 'apple'
fromLang = 'en'
toLang = 'zh'

salt = random.randint(32768, 65536)

sign = appid+q+str(salt)+secretKey
sign = sign.encode('utf-8')
# sign = str(sign)
m1 = hashlib.md5()
m1.update(sign)
sign = m1.hexdigest()
myurl = myurl+'?appid='+appid+'&q='+urllib.parse.quote(q)+'&from='+fromLang+'&to='+toLang+'&salt='+str(salt)+'&sign='+sign
try:
    request = Request(url="http://api.fanyi.baidu.com" + myurl)
    request.add_header('Content-Type', 'application/x-www-form-urlencoded')
    response = urlopen(request)
    content = response.read()
    print(content.decode("unicode-escape"))
except Exception as e:
    print(e)
finally:
    if httpClient:
        httpClient.close()
