import base64
import sys
import json
import time

IS_PY3 = sys.version_info.major == 3

class DemoError(Exception):
    pass

if IS_PY3:
    from urllib.request import urlopen
    from urllib.request import Request
    from urllib.error import URLError
    from urllib.parse import urlencode
    timer = time.perf_counter

API_KEY = 'fWWtDQ79l6Nzzizv74dLC8ch'
SECRET_KEY = 'rbj6g7t2xKSX8xSSRGCLV5NXVsU7efjd'
"""  TOKEN start """

TOKEN_URL = 'http://openapi.baidu.com/oauth/2.0/token'
SCOPE = 'audio_voice_assistant_get'
def fetch_token():
    params = {'grant_type': 'client_credentials',
              'client_id': API_KEY,
              'client_secret': SECRET_KEY}
    post_data = urlencode(params)
    if (IS_PY3):
        post_data = post_data.encode('utf-8')
    req = Request(TOKEN_URL, post_data)
    try:
        f = urlopen(req)
        result_str = f.read()
    except URLError as err:
        print('token http response http code : ' + str(err.code))
        result_str = err.read()
    if (IS_PY3):
        result_str = result_str.decode()

    print(result_str)
    result = json.loads(result_str)
    print(result)
    if ('access_token' in result.keys()):
        print('SUCCESS WITH TOKEN: %s ; EXPIRES IN SECONDS: %s' % (result['access_token'], result['expires_in']))
        return result['access_token']
    else:
        raise DemoError('MAYBE API_KEY or SECRET_KEY not correct: access_token or scope not found in token response')

'''
通用物体和场景识别
'''

request_url = "https://aip.baidubce.com/rest/2.0/image-classify/v2/advanced_general"

# 二进制方式打开图片文件
f = open('img/test.png', 'rb')
img = base64.b64encode(f.read())


params = {"image": img}
params = urlencode(params).encode("utf-8")

access_token = fetch_token()
request_url = request_url + "?access_token=" + access_token
request = Request(url=request_url, data=params)
request.add_header('Content-Type', 'application/x-www-form-urlencoded')
response = urlopen(request)
content = response.read()
if content:
    print(content.decode("utf-8"))
