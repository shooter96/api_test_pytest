import requests
import time
import json
from requests import Response
from utils.test_utils import str_is_none
from utils.test_utils import get_value
import redis

content_type = 'Content-Type'
json_type = 'application/json'
form_type = 'multipart/form-data'


class HttpHandler:

    def __init__(self, case_info):
        """
        持有当前 case_info
        """
        self.case_info = case_info
        self.run_status = None

    def sync_token(self, token, sHost, sPort, sPwd, sDb, dHost, dPort, dPwd, dDb):
        self.s = redis.Redis(host=sHost, port=sPort, password=sPwd, db=sDb, decode_responses=True)
        self.info = self.s.get(token)
        self.d = redis.Redis(host=dHost, port=dPort, password=dPwd, db=dDb, decode_responses=True)
        self.d.setex(token, 10, '' if self.info is None else str(self.info))

    def get_cookie(self):
        """
        获取登录信息
        """
        try:
            result = requests.post(url=self.case_info.host, data=self.case_info.params,
                                   headers=self.case_info.headers)
            if result.status_code == 200:
                cookie_monitoring = result.headers['Set-Cookie'].split(';')[0]
                print('登录成功 Cookie:', cookie_monitoring)
                if self.case_info.host == 'http://10.30.30.31:38080/api/permission/auth/login':
                    self.sync_token(cookie_monitoring.split('=')[1], '10.30.30.31', 6379, '', 15, '10.30.30.96',
                                    26379,
                                    'ZljIsysc0re123', 7)
                return cookie_monitoring
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
        request = self.__build_request()
        if request:
            url, headers, params, files, result = request
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
            result = self.__do_request(url, headers, params, files, result)

            # 计算请求耗时
            time_used = int((time.time() - start) * 1000)
            self.case_info.time_used = time_used
            # 填充结果到用例对象中
            self.case_info.response_content = json.dumps(result, ensure_ascii=False)
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

    def __build_request(self):
        # 得到请求参数
        params = self.case_info.params
        # 定义一个字典，在文件上传时使用
        files = {}
        # 构建请求头
        headers = {}
        if self.case_info.headers:
            headers.update(self.case_info.headers)
        # 请求头没有 Content-Type 默认 json
        if content_type not in headers or headers[content_type] == json_type:
            # 设置为 json
            headers.update({content_type: json_type})
            # 将字典转为字符串
            params = json.dumps(self.case_info.params).encode('utf-8').decode('latin-1')
        # 有 multipart/form-data 的 Content-Type 认为很有可能有文件上传
        elif headers[content_type] == form_type:
            # 上传文件时不需要显示设置 Content-Type
            headers.pop(content_type)
            # 循环 params 字典
            for param in params:
                # 取当前值
                value = params[param]
                # 若值为字符串，并且以 file: 开头，则认为为文件上传
                if isinstance(value, str) and value.startswith('file:'):
                    # 以二进制流加载到 files 中
                    try:
                        files.update({param: open(value.replace('file:', '', 1), 'rb')})
                    except IOError:
                        files.update({param: None})
        # 预先构建结果
        result = {'code': '-1'}
        self.case_info.status = 'failed'
        # 构建 url
        if str_is_none(self.case_info.host):
            result.update({'message': 'host 不能为空'})
            self.case_info.response_content = '请求路径缺失，接口未执行'
            return None
        url = self.case_info.host + self.case_info.path
        return url, headers, params, files, result

    def __do_request(self, url, headers, params, files, result):
        """
        实际请求用例
        """
        # 请求接口

        try:
            # POST
            if self.case_info.method == 'post':
                response = requests.post(url, data=params, headers=headers, files=files)
                result = response.json()
            # GET
            elif self.case_info.method == "get":
                response = requests.get(url, params=params, headers=headers)
                result = response.json()
            # DELETE
            elif self.case_info.method == "delete":
                response = requests.delete(url, data=params, headers=headers)
                result = response.json()
            # PUT
            elif self.case_info.method == "put":
                response = requests.put(url, data=params, headers=headers)
                result = response.json()
            # 未知方法
            else:
                response = Response()
                response.status_code = 200
                result.update({'message': '请求方法不支持，请检查用例'})
            # time.sleep(int(sleep_time))
            # 将请求状态码加入到response
            # result['status_code'] = str(response.status_code)
            # 请求非 200 不处理
            if response.status_code != 200:
                result = {'code': '-1', 'message': '请求失败，请检查用例的请求路径、请求方法、请求参数是否正确'}
        except Exception:
            result.update({'message': '请求失败，请检查用例的请求路径、请求方法、请求参数是否正确'})

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
            # 判断断言的值是否是bool值
            # if isinstance(get_value(result, check_steps[i]), bool):
            #     response.update({expected_keys[i]: get_value(result, check_steps[i])})
            # else:
            #     response.update({expected_keys[i]: str(get_value(result, check_steps[i]))})
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
