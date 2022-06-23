import hashlib
import unittest
import warnings
from pathlib import Path

import requests

url = "http://127.0.0.1:5001"
img_path = "../uploads/steven.jpeg"
user_name = "zeke"
ENCODING = 'utf-8'


def post_send(file, user):
    uri = '/'.join([url, 'upload'])
    path = Path(file)
    payload = {'user_name': user}
    files = [('file', (path.name, open(path.resolve(), 'rb'), 'application/octet-stream'))
             ]
    response = requests.request("POST", uri, data=payload, files=files)
    return response.json()


def get_send(paths):
    uri = '/'.join([url, paths])
    response = requests.request("GET", uri)
    return response


def delete_send(paths):
    uri = '/'.join([url, 'delete', paths])
    response = requests.request("DELETE", uri)
    return response


def pic_encode(path):
    with open(path, 'rb') as f:
        md5 = hashlib.md5(f.read()).hexdigest()
    # permacache = pickle.load(f)
    warnings.simplefilter('ignore', )

    return md5


class TestPicBed(unittest.TestCase):
    def test_1_it_work(self):
        # print(get_send('ping'))
        self.assertEqual('pong!', get_send('ping').text, 'Not work')

    def test_2_post(self):
        md5 = pic_encode(img_path)
        r = post_send(img_path, user_name)
        pic_path = str(r['uri'])

        self.assertEqual(md5, Path(pic_path).stem, 'post err')

    def test_3_get(self):
        uri = 'zeke/202206/99bd177d4ba0082c32e49b3d26e7b62b.jpeg'
        r = get_send(uri)
        self.assertEqual(True, r.ok, 'get error\nstatus_code = {}'.format(r.status_code))

    def test_4_delete(self):
        uri = 'zeke/202206/99bd177d4ba0082c32e49b3d26e7b62b.jpeg'
        r = delete_send(uri)
        self.assertEqual(True, r.ok, 'delete error\nstatus_code = {}'.format(r.status_code))


if __name__ == '__main__':
    unittest.main()
