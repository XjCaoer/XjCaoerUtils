# -*- coding: utf-8 -*-
import os
import requests
import base64
import sys
import uuid
import hashlib
from imp import reload
import time
import re
import string

reload(sys)

##================================================================================##
"""有道云OCR"""
def truncate(q):
    if q is None:
        return None
    size = len(q)
    return q if size <= 20 else q[0:10] + str(size) + q[size - 10:size]


def encrypt(signStr):
    hash_algorithm = hashlib.sha256()
    hash_algorithm.update(signStr.encode('utf-8'))
    return hash_algorithm.hexdigest()


def do_request(data):
    YOUDAO_URL = 'https://openapi.youdao.com/ocrapi'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    return requests.post(YOUDAO_URL, data=data, headers=headers)


def connect(file):
    f = open(file, 'rb')  # 二进制方式打开图文件
    APP_KEY = '3f062dd3b08a56b3'
    APP_SECRET = 'UNYm9JCzQ9YLjexZq6F1v3R48phXM0Kz'
    q = base64.b64encode(f.read()).decode('utf-8')  # 读取文件内容，转换为base64编码
    f.close()

    data = {}
    data['detectType'] = '10012'
    data['imageType'] = '1'
    data['langType'] = 'auto'
    data['img'] = q
    data['docType'] = 'json'
    data['signType'] = 'v3'
    curtime = str(int(time.time()))
    data['curtime'] = curtime
    salt = str(uuid.uuid1())
    signStr = APP_KEY + truncate(q) + salt + curtime + APP_SECRET
    sign = encrypt(signStr)
    data['appKey'] = APP_KEY
    data['salt'] = salt
    data['sign'] = sign

    response = do_request(data)
    resjson = response.json()
    res = ""
    if resjson:
        if 'Result' in resjson and resjson['Result']['regions']:
            locList = resjson['Result']['regions'][0]['lines']
            if locList:
                for i in locList:
                    res += i['text'].strip()
    return res
    

##================================================================================##
"""百度OCR图片文字识别"""
def BaiDuRecog(url):
    request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/webimage"
    f = open(url, 'rb')
    img = base64.b64encode(f.read())
    
    params = {"image":img, 'language_type':'auto_detect'}
    access_token = "24.81d110c24f917874be25f60ff3df9dc5.2592000.1624707951.282335-24260132"
    
    request_url = request_url + "?access_token=" + access_token
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.post(request_url, data=params, headers=headers)
    res = ""
    if response:
        if 'words_result' in response.json():
            
            locList = response.json()['words_result']
            if locList:
                for i in locList:
                    res += i['words'].strip()
    return res


##================================================================================##
"""语言检测"""
remove_nota = u'[’·°–!"#$%&\'()*+,-./:;<=>?@，。?★、…【】（）《》？“”‘’！[\\]^_`{|}~]+'
remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)
def filter_str(sentence):
    sentence = re.sub(remove_nota, '', sentence)
    sentence = sentence.translate(remove_punctuation_map)
    return sentence.strip()
    
# 判断是否韩文
def judge_language(s):
    s = filter_str(s)
    s = re.sub('[0-9]', '', s).strip()


    # unicode korean
    re_words = re.compile(u"[\uac00-\ud7ff]+")
    res = re.findall(re_words, s)  # 查询出所有的匹配字符串
    if len(res) > 0:
        return 'ko'

 ##================================================================================##
#　获取批量图片文件并识别
def recogPhotoFiles(directory, outputTxt):
        f = open(outputTxt, 'w', encoding = 'utf-8')
        files = os.listdir(directory)
        count = 0
        for file in files:
            # res = BaiDuRecog(directory + file)
            res = connect(directory + file)
            print("图片：%s ——————" % file)
            if res and judge_language(res):
                f.write(file + '\t')
                print(res)
                f.write(res)
                count += 1
                f.write('\n')
        print("共识别出"+ str(count) + "张图片")
        f.close()

 
if __name__=="__main__":
    directory = "./1/"  # 图片文件夹
    outputTxt = "result.txt"  # 结果文件
    recogPhotoFiles(directory, outputTxt)
    
