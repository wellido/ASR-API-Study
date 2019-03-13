from aip import AipImageClassify


def ir_api(image):
    """ 你的 APPID AK SK """
    APP_ID = '15719765'
    API_KEY = 'W3gO6OKVcKtGSGtIjN2rTZgW'
    SECRET_KEY = '2T1cZrytwBGLLrjFosQjNvSczgIufLg2'

    client = AipImageClassify(APP_ID, API_KEY, SECRET_KEY)

    """ 调用通用物体识别 """
    client.advancedGeneral(image)

    """ 如果有可选参数 """
    options = {}
    options["baike_num"] = 5

    """ 带参数调用通用物体识别 """
    result = client.advancedGeneral(image, options)['result']
    obj_type = result[0]['root']
    obj_confidence = result[0]['score']

    print("object type: ", obj_type)
    print("object confidence: ", obj_confidence)
    return obj_type, obj_confidence


if __name__ == '__main__':
    """ 读取图片 """
    def get_file_content(filePath):
        with open(filePath, 'rb') as fp:
            return fp.read()
    image = get_file_content('../data/img/20180423_004214_sea_lion.png')
    ir_api(image)
