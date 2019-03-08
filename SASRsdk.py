# -*- coding:utf-8 -*-
# import urllib2
import urllib
import hmac
import hashlib
import base64
import time
import random


def formatSignString(param):
    signstr = "POSTaai.tencentcloudapi.com/?"
    for x in param:
        tmp = x
        for t in tmp:
            signstr += str(t)
            signstr += "="
        signstr = signstr[:-1]
        signstr += "&"
    signstr = signstr[:-1]
    # print 'signstr',signstr
    return signstr


def sign(signstr, secret_key):
    hmacstr = hmac.new(secret_key, signstr, hashlib.sha1).digest()
    s = base64.b64encode(hmacstr)
    print('sign: ', s)
    return s


def formparam(param, signs):
    body = ""
    for x in param:
        tmp = x
        for t in tmp:
            body += urllib.parse.quote(str(t), "")
            body += "="
        body = body[:-1]
        body += "&"
    body += "Signature="
    body += signs
    # print 'body: ',body
    return body


def rand(n):
    seed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    sa = []
    for i in range(n):
        sa.append(random.choice(seed))
    salt = ''.join(sa)
    # print salt
    return salt


def sentVoice(secretKey, SecretId, EngSerViceType, SourceType, URI, VoiceFormat):
    if len(str(secretKey)) == 0:
        print('secretKey can not empty')
        return
    if len(str(SecretId)) == 0:
        print('SecretId can not empty')
        return
    if len(str(EngSerViceType)) == 0 or (str(EngSerViceType) != '8k' and str(EngSerViceType) != '16k'):
        print('EngSerViceType is not right')
        return
    if len(str(SourceType)) == 0 or (str(SourceType) != '0' and str(SourceType) != '1'):
        print('SourceType is not right')
        return
    if len(str(URI)) == 0:
        print('URI can not empty')
        return
    if len(str(VoiceFormat)) == 0 or (str(VoiceFormat) != 'mp3' and str(VoiceFormat) != 'wav'):
        print('VoiceFormat is not right')
        return

    secret_key = secretKey
    query_arr = dict()
    query_arr['Action'] = 'SentenceRecognition'
    query_arr['SecretId'] = SecretId
    query_arr['Timestamp'] = str(int(time.time()))
    query_arr['Nonce'] = query_arr['Timestamp'][0:4]
    query_arr['Version'] = '2018-05-22'
    query_arr['ProjectId'] = 0
    query_arr['SubServiceType'] = 2
    query_arr['EngSerViceType'] = EngSerViceType
    query_arr['SourceType'] = SourceType
    if (query_arr['SourceType'] == 0):
        voice = URI
        voice = urllib.parse.quote(voice, "")
        query_arr['Url'] = voice
    else:
        file_path = URI
        file_object = open(file_path, 'rb')
        content = file_object.read()
        query_arr["DataLen"] = len(content)
        basecontent = base64.b64encode(content)
        query_arr["Data"] = basecontent
        # print(len(content))
        file_object.close()

    query_arr['VoiceFormat'] = VoiceFormat
    query_arr['UsrAudioKey'] = rand(16)
    query = sorted(list(query_arr.items()), key=lambda d: d[0])
    signstr = formatSignString(query)
    signpre = sign(signstr, secret_key)
    signs = urllib.parse.quote(signpre, "")
    bodystr = formparam(query, signs)
    requrl = "https://aai.tencentcloudapi.com"
    headers = {'Host': 'aai.tencentcloudapi.com', 'Content-Type': 'application/x-www-form-urlencoded',
               'charset': 'UTF-8'}
    req = urllib.request.Request(requrl, data=bodystr, headers=headers)
    res_data = urllib.request.urlopen(req)
    res = res_data.read()
    print(res)
    return
