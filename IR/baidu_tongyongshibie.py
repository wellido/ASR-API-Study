from aip import AipImageClassify

""" 你的 APPID AK SK """
APP_ID = '15719765'
API_KEY = 'W3gO6OKVcKtGSGtIjN2rTZgW'
SECRET_KEY = '2T1cZrytwBGLLrjFosQjNvSczgIufLg2'

client = AipImageClassify(APP_ID, API_KEY, SECRET_KEY)

""" 读取图片 """
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

image = get_file_content('C:\\Users\\tencon2010\\Desktop\\20150620224348_ajx2z.jpeg')

""" 调用通用物体识别 """
client.advancedGeneral(image);

""" 如果有可选参数 """
options = {}
options["baike_num"] = 5

""" 带参数调用通用物体识别 """
print(client.advancedGeneral(image, options))
