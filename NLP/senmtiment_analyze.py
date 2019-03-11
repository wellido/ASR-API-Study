from aip import AipNlp

""" 你的 APPID AK SK """
APP_ID = '15732335'
API_KEY = '22Gb3zjNqTNuwYGZ6TfWHTtH'
SECRET_KEY = 'WLwdhdLfMVA1YehjM2xnPMDOUvQPRPgr'

client = AipNlp(APP_ID, API_KEY, SECRET_KEY)

# 输入
text = "苹果是一家伟大的公司"

""" 调用情感倾向分析 """
result = client.sentimentClassify(text)
print(result)
