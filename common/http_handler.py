# @author: wy
# @project:api_test_pytest
import json
import time

from common.utils_handler import get_value

import requests


# 请求方法封装，普通get(表单、路径传参)、post（普通body传参、文件上传）、put、delete等方法封装
class HttpRequest:
    def __init__(self, case_info):
        self.method = case_info.method
        self.params = case_info.params
        self.headers = case_info.headers
        self.url = case_info.url
        self.response = {}
        self.case_info = case_info

    def http_request(self, files):
        """
        封装请求方法
        """

        if files:
            if self.method == 'post':
                self.response = requests.post(url=self.url, data=self.params, headers=self.headers, files=files)
            elif self.method == 'put':
                self.response = requests.put(url=self.url, data=self.params, headers=self.headers, files=files)
        else:
            if self.method == 'post':
                self.response = requests.post(url=self.url, json=self.params, headers=self.headers)
            elif self.method == 'put':
                self.response = requests.put(url=self.url, json=self.params, headers=self.headers)
            elif self.method == 'get':
                self.response = requests.get(url=self.url, params=self.params, headers=self.headers)
            elif self.method == 'delete':
                self.response = requests.delete(url=self.url, params=self.params, headers=self.headers)

        return self.response.json()

    def build_request(self):
        """
        1、更新请求头
        2、 判断请求头类型，对请求体进行数据类型处理
        3、更新用例是否执行的标签
        """
        # 获取到请求参数,字典类型
        params = self.case_info.params
        # 构建请求头
        headers = {}
        # 定义一个字典，用于文件上传
        files = {}
        if self.case_info.headers:
            headers.update(self.case_info.headers)
        if 'Content-Type' not in self.case_info.headers:
            # 如果excel中的headers为空则设为json格式
            headers['Content-Type'] = 'application/json'

        else:
            # 否则为表单形式
            headers['Content-Type'] = 'multipart/form-data'
            # 循环字典,拿到字典最外层的key
            for param in params:
                # 判断是否为文件上传
                value = params[param]
                if str(value).startswith('file:'):
                    try:
                        # 以二进制流加载到files中
                        files[param] = open(str(value).split(':')[1], mode='rb')
                    except IOError:
                        files.update({param: None})
        url = self.case_info.host + self.case_info.path
        return url, headers, params, files

    def get_token(self):
        """
        获取登录信息
        """
        try:
            result = requests.post(url=self.url, data=self.params,
                                   headers=self.headers)
            if result.status_code == 200:
                token = result.json()['data']['token']
                print('登录成功 token:', token)
                # return cookie_monitoring
                return token
            else:
                raise Exception
        except Exception as e:
            print('登录产生异常', e)
            return ''

    def execute(self, case_infos):
        """
        执行请求
        """
        # 构建请求参数
        request = self.build_request()
        result = {}
        if request:
            url, headers, params, files = request
            self.url = url
            self.params = params
            self.headers = headers
            self.files = files

        else:
            return None
        # 请求开始时间
        start = time.time()

        # 判断请求完成后是否需要等待
        sleep_time = 0 if self.case_info.sleep is None or self.case_info.sleep == ' ' \
            else self.case_info.sleep

        # 判断用例是否需要执行
        run_status = "yes" if self.case_info.run is None or self.case_info.run == ' ' \
            else self.case_info.run
        self.run_status = run_status.lower()
        if self.run_status == 'yes':
            # 请求
            result = self.http_request(self.files)

            # 计算请求耗时
            time_used = int((time.time() - start) * 1000)
            self.case_info.time_used = time_used
            # 填充结果到用例对象中
            self.case_info.response_content = json.dumps(result, ensure_ascii=False)
            # 用于后续参数化传递依赖值的目标
            # self.case_info.sheet_content[
            #     self.case_info.sheet_name + "-" + str(self.case_info.row)] = self.case_info.response_content
            if 'code' in result.keys():
                code = result['code']
                # 防止 code 为字符串类型的数字
                self.case_info.response_code = code if isinstance(code, int) else int(code)
            # 校验结果
            self.__check_status(result, case_infos)
            # print 结果
            self.__print_result(url)
            # 等待
            time.sleep(int(sleep_time))
        else:
            self.case_info.status = '未执行'
        return result

    def __check_status(self, result, case_infos):
        """
        校验结果

        思路：
        让预期值为一个字典
        实际值为另一个字典
        对比字典内容是否一致，从而确定结果是否符合预期
        """
        # 定义预期和结果字典
        expected = {}
        response = {}
        # 预期字段以 , 分割为预期字段的列表
        expected_keys = self.case_info.expected_key.split(',')
        # 预期结果以 , 分割为预期结果的列表
        expected_values = str(self.case_info.expected_value).split(',')
        # 校验步骤以 , 分割为列表
        check_steps = self.case_info.check_step.split(',')
        # 循环预期字段的个数
        for i in range(0, len(expected_keys)):
            # 将预期字段对应的预期值以 : 分割，得到预期值的取值过程列表
            row_steps = expected_values[i].split(":")
            # 如果预期值直接给出，则 row_steps 长度为 1
            if len(row_steps) == 1:
                # 将预期字段以及预期值放入预期字典
                expected.update({expected_keys[i]: row_steps[0]})
            else:
                # 取依赖的行数据
                ci = [ci for ci in case_infos if getattr(ci, 'row') == int(row_steps[0])]
                ci = ci[0]
                # 没取到直接判定失败
                if not ci:
                    self.case_info.status = 'failed'
                    return
                # 否则按照依赖步骤取出依赖值，填充预期字典
                ci = json.loads(getattr(ci, 'response_content'))
                expected.update({expected_keys[i]: get_value(ci, row_steps[1])})
            response.update({expected_keys[i]: str(get_value(result, check_steps[i]))})
            # 填入结果
            if expected == response:
                self.case_info.status = 'passed'
            else:
                self.case_info.status = 'failed'

    def __print_result(self, url):
        """
        打印请求结果
        """
        out = json.dumps({'用例行号': self.case_info.row + 1, '用例': self.case_info.description, '步骤': self.case_info.step,
                          '请求方式': self.case_info.method, '请求路径': url, '请求结果': self.case_info.status}, indent=2,
                         ensure_ascii=False)
        if self.case_info.status == 'passed':
            out = out.replace('passed', '\033[0;33;42m' + 'passed' + '\033[0m')
        else:
            out = out.replace('failed', '\033[0;37;41m' + 'failed' + '\033[0m')
        print(out, flush=True)
