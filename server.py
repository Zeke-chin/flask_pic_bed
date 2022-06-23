import base64
import hashlib
import logging
import os
import re
from base64 import b64encode
from pathlib import Path
from time import strftime, localtime

from flask import Flask, request, Response, jsonify
from flask import current_app
from flask import json
from werkzeug.exceptions import HTTPException
from werkzeug.utils import secure_filename

ENCODING = 'utf-8'
UPLOAD_FOLDER = 'uploads'
# 上传路径
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
# 允许格式

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# 健康检查接口
@app.route('/ping')
def index():
    app.logger.info('pong！')
    return "pong!"


# 检测文件名是否合法
def allowed_file(filename):
    linux_file_allowed = "^[^+-./\t\b@#$%*()\[\]][^/\t\b@#$%*()\[\]]{1,254}$"
    filename_suffix = re.match(linux_file_allowed, filename)
    allowed_suffix = '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    return filename_suffix and allowed_suffix


# 创建用户目录
def user_file(user):
    First_dir = user
    # zeke
    Second_dir = str(strftime('%Y%m', localtime()))
    # 202206
    path = Path(app.config['UPLOAD_FOLDER']) / First_dir / Second_dir
    # uploads/zeke/202206

    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)
    return path


# 文件上传接口
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        # 检测 post 是否有文件
        raise Exception('No file part')

    file = request.files['file']
    user_name = request.form['user_name']
    # 获得这个 文件、用户名

    if file and allowed_file(file.filename):
        # 文件 和 文件拓展名 都 没有问题

        path = user_file(user_name)
        # 创建user目录 uploads/zeke/202206

        filename = secure_filename(file.filename)
        # 获取文件名 xxx.jpg

        filename_md5 = '.'.join([hashlib.md5(file.read()).hexdigest(), filename.split('.')[-1]])
        # 获取md5文件名 b16e8e30c0883622a95cdf8d50334abd.jpg

        uri = str(Path(path) / filename_md5)
        file.seek(0)
        # uploads/zeke/202206/b61...abd.jpg

        file.save(uri)
        # 保存文件
        app.logger.info('POST ==> {}-{}'.format(user_name, filename))
        return jsonify(uri=uri)
        # uploads/zeke/202206/b16e8e30c0883622a95cdf8d50334abd.JPG

    else:
        return 'File_Name illegal'


# GET 接口
@app.route('/<path:uri>', methods=['GET'])
def get_frame(uri):
    image_data = img_cache(uri)
    # 二进制图片
    request_get = Response(image_data, mimetype='image/jpg')
    app.logger.info('GET ==> {}'.format(uri))
    return request_get


# 删除接口
@app.route('/delete/<path:uri>', methods=['DELETE'])
def delete_frame(uri):
    img_path = '/'.join(['uploads', uri])
    delete_status = os.path.exists(img_path)
    if delete_status:
        os.remove(img_path)
        del cache[uri.split('/')[-1]]
        app.logger.info('DELETE ==> {}'.format(img_path))
    return jsonify(delete_status=str(delete_status))


# 编码
def pic_encode(image):
    base64_bytes = b64encode(image)
    base64_string = base64_bytes.decode(ENCODING)
    return base64_string


# 解码
def pic_decode(value):
    image_data = base64.b64decode(value)
    return image_data


# 缓存器
cache = {}


# 缓存装饰器
def fifo_cache(func):
    def inner(url):
        key = url.split('/')[-1]
        value = cache.get(key)
        if value is not None:
            app.logger.info('hit ==> {}'.format(key))
            image_data = pic_decode(value)
        else:
            app.logger.info('miss ==> {}'.format(key))
            image_data = func(url)
            cache[key] = pic_encode(image_data)

        return image_data

    return inner


# GET 接口缓存
@fifo_cache
def img_cache(uri):
    with open(r'uploads/{}'.format(uri), 'rb') as f:
        image_data = f.read()
    return image_data


# 网页图标请求处理
@app.route('/favicon.ico')
def get_fav():
    return current_app.send_static_file('img/favicon.ico')


# 通用错误处理
@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response


if __name__ == '__main__':
    handler = logging.FileHandler('flask.log', encoding='UTF-8')
    # 创建一个log handler

    logging_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
    handler.setFormatter(logging_format)
    # 日志时间 - 日志等级 - 触发日志python文件名 - 触发日志函数名 - 触发代码行号 - app.logger.info(messages)

    app.logger.setLevel(logging.INFO)
    # 日志等级
    app.logger.addHandler(handler)
    # 即将此handler加入到此app中

    app.run(host='0.0.0.0', port=5000)
