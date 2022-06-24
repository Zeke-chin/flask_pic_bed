import base64
import logging
from base64 import b64encode

from flask import Flask, request, Response, jsonify
from flask import current_app
from flask import json
from werkzeug.exceptions import HTTPException

from config.config import config
from file_manager.file_manager import FileManager

app = Flask(__name__)
app.config.from_object(config)


# 健康检查接口
@app.route('/ping')
def index():
    app.logger.info('pong！')
    return "pong!"


Flask_File = FileManager()


# 文件上传接口
@app.route('/upload', methods=['POST'])
def upload_file():
    # request 解析
    files = request.files
    # ImmutableMultiDict([('file', <FileStorage: 'steven.jpeg' ('application/octet-stream')>)])
    file = request.files['file']
    # <FileStorage: 'steven.jpeg' ('application/octet-stream')>
    file_name = request.files['file'].filename
    # 'steven.jpeg'
    file.seek(0)
    # '99bd177d4ba0082c32e49b3d26e7b62b.jpeg'
    user_name = request.form['user_name']
    # 'zeke'

    # 检测 post 是否有文件
    if 'file' not in files:
        raise Exception('No file part')

    if file and Flask_File.allowed_file(file_name):
        # 文件 和 文件拓展名 都 没有问题

        uri = Flask_File.save(user_name, file)
        # 保存文件 并 返回 uri

        app.logger.info('POST ==> {}-{}'.format(user_name, file_name))
        return jsonify(uri=uri)
        # uploads/zeke/202206/b16e8e30c0883622a95cdf8d50334abd.JPG
    else:
        return 'File_Name illegal'


# GET 接口
@app.route('/<path:uri>', methods=['GET'])
def get_frame(uri):
    # 'zeke/202206/99bd177d4ba0082c32e49b3d26e7b62b.jpeg'
    image_data = Flask_File.get(uri)
    # 二进制图片

    request_get = Response(image_data, mimetype='image/jpg')
    app.logger.info('GET ==> {}'.format(uri))
    return request_get


# 删除接口
@app.route('/delete/<path:uri>', methods=['DELETE'])
def delete_frame(uri):
    # 'zeke/202206/99bd177d4ba0082c32e49b3d26e7b62b.jpeg'
    img_path = '/'.join(['uploads', uri])
    # 'uploads/zeke/202206/99bd177d4ba0082c32e49b3d26e7b62b.jpeg'

    img_status = Flask_File.delete(img_path)
    return jsonify(img_status=img_status)


# 缓存器
class Cache:

    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, url):
        key = url.split('/')[-1]
        value = self.cache.get(key)
        if value is not None:
            app.logger.info('GET_hit ==> {}'.format(key))
            image_data = self.pic_decode(value)
        else:
            app.logger.info('GET_miss ==> {}'.format(key))
            image_data = self.func(url)
            self.cache[key] = self.pic_encode(image_data)

        return image_data

    def delete(self, url):
        key = url.split('/')[-1]
        app.logger.info('DELETE_Cache ==> {}'.format(key))
        del self.cache[key]

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


@Cache
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

    app.run(host='0.0.0.0', port=5000, debug=True)
