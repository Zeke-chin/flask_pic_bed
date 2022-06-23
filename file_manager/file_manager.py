import base64
import hashlib
import os
import re
from base64 import b64encode
from pathlib import Path
from time import strftime, localtime

from flask import Flask, request, Response, jsonify
from flask import current_app
from flask import json
from werkzeug.exceptions import HTTPException

from flask_pic_bed import config

app = Flask(__name__)
app.config.from_object(config)


class FileManager:

    def __init__(self):
        self.cache = {}

    # 存图片
    def save(self, username, file):
        path = self.user_file(username)
        # 创建user目录 uploads/zeke/202206

        filenamemd5 = '.'.join([hashlib.md5(file.read()).hexdigest(), file.filename.split('.')[-1]])
        uri = str(Path(path) / filenamemd5)
        file.save(uri)
        app.logger.info('POST ==> {}-{}'.format(username, file.filename))
        return uri

    # 取图片(带缓存)
    def get(self, uri):
        key = uri.split('/')[-1]
        value = self.cache.get(key)
        if value is not None:
            app.logger.info('GET_hit ==> {}'.format(key))
            image_data = self.pic_decode(value)
        else:
            app.logger.info('GET_miss ==> {}'.format(key))
            with open(r'uploads/{}'.format(uri), 'rb') as f:
                image_data = f.read()
                self.cache[key] = self.pic_encode(image_data)

        return image_data

    # 删图片(带缓存)
    def delete(self, path):
        # 'uploads/zeke/202206/99bd177d4ba0082c32e49b3d26e7b62b.jpeg'
        img_status = os.path.exists(path)
        if img_status:
            os.remove(path)
            key = path.split('/')[-1]
            del self.cache[key]
            app.logger.info('DELETE ==> {}'.format(path))
        return str(img_status)

    # 检测 文件名和文件后缀
    @staticmethod
    def allowed_file(filename):
        linux_file_allowed = "^[^+-./\t\b@#$%*()\[\]][^/\t\b@#$%*()\[\]]{1,254}$"
        filename_suffix = re.match(linux_file_allowed, filename)
        allowed_suffix = '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config[
            'ALLOWED_EXTENSIONS']
        return filename_suffix and allowed_suffix

    # 创建用户目录
    @staticmethod
    def user_file(username):
        First_dir = username
        # zeke
        Second_dir = str(strftime('%Y%m', localtime()))
        # 202206
        path = Path(app.config['UPLOAD_FOLDER']) / First_dir / Second_dir
        # uploads/zeke/202206

        folder = os.path.exists(path)
        if not folder:
            os.makedirs(path)
        return path

    @staticmethod
    # b64编码
    def pic_encode(image):
        base64_bytes = b64encode(image)
        base64_string = base64_bytes.decode(app.config['ENCODING'])
        return base64_string

    @staticmethod
    # b64解码
    def pic_decode(value):
        image_data = base64.b64decode(value)
        return image_data
