# # -*- coding:utf-8 -*-
# # 引入 SDK
# import SASRsdk
#
# # 用户需修改为自己官网的secretid与sectretkey
# secretKey = 'AKIDgGMR4SCO4E9WoNtkaYgJNpHWr36ncr1g'
# SecretId = 'a8a0C2fslvpU6UMBsoWSCXzIT5nHfvAA'
#
# # 识别引擎 8k or 16k
# EngSerViceType = '16k'
# # 语音数据来源 0:语音url or 1:语音数据 bodydata
# SourceType = 1
# # 语音数据地址
# URI = 'wav/extra_0a.wav'
# # URI='http://liqiansunvoice-1255628450.cosgz.myqcloud.com/30s.wav'
# # 音频格式 mp3 or wav
# VoiceFormat = 'wav'
# # 调用 sentVoice 函数获得识别结果
# SASRsdk.sentVoice(secretKey, SecretId, EngSerViceType, SourceType, URI, VoiceFormat)
import random
import hmac
import base64
import hashlib
import time
import requests
import urllib.parse

class AipBase(object):
    """
        AipBase
    """

    def __init__(self, appId, secretId, secretKey):
        """
            AipBase(appId,secretId,secretKey)
        """
        self._appID = appId
        self._secretId = secretId.strip()
        self._secretKey = secretKey.strip()
        self.__version = '1.0.0'

    def getVersion(self):
        return self.__version
    # 生成随机字符串
    def getrandom(self,length):
        nonce = ''
        for i in range(length):
            number = random.randint(1, 9)
            nonce = nonce + str(number)
        return int(nonce)

    # 字典排序算法
    def sordict(self,dict):
        after = sorted(zip(dict.keys(), dict.values()))
        return after

    # 算法参考地址
    # http://outofmemory.cn/code-snippet/33173/python-hmac-sha1
    def encrypt(self,signature1, secretkey):
        signature = bytes(signature1, encoding='utf-8')
        secretkey = bytes(secretkey, encoding='utf-8')
        # 这里python跟其他语言的写法不太一样。密钥在第一位，第二位才是要加密的。而且是bytes类型加密
        my_sign = hmac.new(secretkey, signature, hashlib.sha1).digest()
        my_sign = base64.b64encode(my_sign)
        return my_sign

# 官方文档地址：
# https://cloud.tencent.com/document/product/441/17366
# https://cloud.tencent.com/document/product/441/6201
class AipSpeech(AipBase):
    __requestVoiceUrl = 'http://aai.qcloud.com/asr/v1/'
    __signaturehead = 'POSTaai.qcloud.com/asr/v1/'

    # 拼接参数
    def sortparms(self, callback_url, projectid =0, engine_model_type="16k_0", res_text_format=0, source_type=1):
        """
        :param callback_url: 回调地址
        :param secretid: 在控制台“云API密钥”获得
        :param secretkey: 在控制台“云API密钥”获得
        :param projectid:  项目id, 默认0为默认项目
        :param engine_model_type:
        :param res_text_format:
        :param source_type:
        :return:
        """
        timestamp = int(time.time())  # 当前时间的时间戳
        expired = timestamp + 10000  # 签名有效期
        nonce = super(AipSpeech, self).getrandom(6)  # 随机正整数。用户需自行生成，最长 10 位
        app_id = self._appID  # 1256603936
        projectid = 0
        secretkey = self._secretKey
        secretid = self._secretId
        keydict = {
            "projectid": projectid,
            "sub_service_type": 0,
            "engine_model_type": engine_model_type,
            # 语音 URL，公网可下载。当 source_type 值为 0 时须填写该字段，为 1 时不填；URL 的长度大于 0，小于 2048
            # "url": "http://test.qq.com/rec_callback",
            "res_text_format": 0,
            "res_type": 1,
            "callback_url": "http://ksp2tc.natappfree.cc/test",
            "source_type": source_type,
            "secretid": secretid,
            "timestamp": timestamp,
            "expired": expired,
            "nonce": nonce,
        }
        # 字典排序后的字典
        sortkeydict = super(AipSpeech, self).sordict(keydict)
        return sortkeydict

    # 生成签名
    def keygen(self,sortkeydict):
        afterstr = ''
        for i in sortkeydict:
            afterstr = afterstr + str(i[0]) + '=' + str(i[1]) + '&'
        keystr = self.__signaturehead + str(self._appID) + '?'
        signature1 = (keystr + afterstr[:-1])
        print('拼接后的字符串', signature1)
        # 加密处理后，得到签名字符串
        # 签名字符可以保存，下次直接使用。因为签名可以设置有效期，不超过90天
        signature_str = super(AipSpeech, self).encrypt(signature1, self._secretKey)
        # 返回签名
        return signature_str

    # 语音识别接口访问，上传本地文件。url形式的上传可以参考官方文档。
    def request2getjob_id(self,signature_str, app_id, filepath, sortkeydict):
        """
        :param signature_str: j加密后的签名
        :param app_id:   appid ,在控制台“云API密钥”获得
        :param filepath:  本地音频文件路径
        :param sortkeydict: 访问语音API需要的参数列表，已经过字典排序
        :return: job_id 任务id，用于获取语音结果。
        """

        body = ''
        with open(filepath, 'rb') as f:
            body = f.read()
        header = {
            "Host": "aai.qcloud.com",
            "Content-Type": "application/octet-stream",
            "Authorization": signature_str,
            "Content-Length": str(len(body)),
        }
        url = self.__requestVoiceUrl + str(app_id) + '?' + urllib.parse.urlencode(sortkeydict)
        print(url)
        response = requests.post(url, data=body, headers=header)
        if response.status_code == 200:
            print("上传识别音频文件成功")
            result = eval(str(response.content))
            result_str = str(result, 'utf-8')
            job_id = result_str[result_str.index("Id") + 4: result_str.index("}")]
            print(job_id)
            # 任务ID
            job_id = int(job_id)
            # job_id = result.get("requestid")
            return job_id
        else:
            print("失败")
            # 根据返回的code去腾讯的文档中心来查看是哪一步出错了
            # https://cloud.tencent.com/document/product/441/6201
            print(response.content)
            return 0
        return 0



if __name__ == "__main__":
    call_url = "http://ksp2tc.natappfree.cc/test"
    speech = AipSpeech(1258780747, "AKIDgGMR4SCO4E9WoNtkaYgJNpHWr36ncr1g", "a8a0C2fslvpU6UMBsoWSCXzIT5nHfvAA")
    sortkeydict = speech.sortparms(call_url)
    print(sortkeydict)
    signature_str = speech.keygen(sortkeydict)
    speech.request2getjob_id(signature_str, speech._appID, "wav/extra_0a.wav", sortkeydict)



