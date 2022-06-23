# 图床

基于 Flask，用于图片的网络储存

- 上传：使用用户名和时间做目录名实现多空间存储
- 下载：拥有缓存机制的下载
- 删除：删除指定用户的指定图片

## 环境

- python >= 3.8.13
- Flask >= 2.1.2
- requests

```bash
pip install -r requirements.txt
```

## 启动服务

```python
# 启动服务 port 5000
python server.py
```

## 单元测试

```python
 python -m unittest discover testing server_test.py -v
```

