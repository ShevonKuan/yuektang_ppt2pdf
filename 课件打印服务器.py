from flask import Flask, request
import json
import re
import requests
import os
import time
from PIL import Image
import tqdm
import shutil
import logging
app = Flask(__name__)

log = logging.getLogger('werkzeug')
log.disabled = True


def outpdf(title, urls):
    '''下载图片合并为pdf'''
    os.makedirs('tmp/'+title)
    PathList = []
    print('开始下载图片')
    for index, url in tqdm.tqdm(enumerate(urls)):  # 图片下载
        path = 'tmp/' + title + '/' + str(index)+'.png'
        r = requests.get(url, stream=True)
        PathList.append(path)
        open(path, 'wb').write(r.content)
    file = Image.open(PathList[0])

    ImageList = []
    print('正在转换图片')
    for index in range(1, len(PathList)):  # 图片读取
        image = Image.open(PathList[index])
        if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
            image = image.convert('RGB')
        ImageList.append(image)

    # pdf合成
    print('开始合并为pdf')
    file.save(title+'.pdf', 'PDF', resolution=100.0,
              save_all=True, append_images=ImageList)
    print('完成pdf导出')


@app.route('/print', methods=['post'])
def index():
    data = json.loads(request.get_data())
    try:
        outpdf(data['title'], data['link'])
        shutil.rmtree("tmp")  # 执行完成删除缓存
        return json.dumps({'status': 'ok'})
    except:
        shutil.rmtree("tmp")
        return json.dumps({'status': 'err'})


@app.route('/', methods=['get'])
def pulse():
    # 服务器心跳检测
    return json.dumps({'status': 'ok'})


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=63321)
