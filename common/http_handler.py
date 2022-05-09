# @author: wy
# @project:api_test_pytest
import requests


# 请求方法封装，普通get(表单、路径传参)、post（普通body传参、文件上传）、put、delete等方法封装
class HttpRequest:
    def __init__(self, case_info):
        self.method = case_info.method
        self.url = case_info.url
        self.params = case_info.params
        self.headers = case_info.headers
        self.files = case_info.files
        self.response = {}

    def build_request(self):
        """
        1、更新请求头
        2、 判断请求头类型，对请求体进行处理
        """

    def do_request(self):
        """
        封装请求方法
        """
        if self.method == 'post':
            self.response = requests.post(url=self.url, data=self.params, headers=self.headers, files=self.files)
        elif self.method == 'get':
            self.response = requests.get(url=self.url, params=self.params, headers=self.headers)
        elif self.method == 'put':
            self.response = requests.put(url=self.url, data=self.params, headers=self.headers, files=self.files)
        elif self.method == 'delete':
            self.response = requests.delete(url=self.url, params=self.params, headers=self.headers)

        return self.response.json()
