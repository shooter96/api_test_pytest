# @author: wy
# @project:api_test_pytest
import json

from common.excel_handler import ExcelHandler, CaseInfoHandler
from common.http_handler import HttpRequest
from common.path_handler import *
import os


# 获取测试用例
# 根据服务名和版本号获取
def getCasesInfoFromExcel(service_name, version='latest'):
    excel_data_dir = EXCEL_PATH + '/' + service_name + '/latest'
    # version默认取最新的版本
    file_list = os.listdir(excel_data_dir)
    for file in file_list:
        src = excel_data_dir + '/' + file
        # 打开源 Excel 工作簿
        excel_handler = ExcelHandler(src)
        # 获取excel中所有的sheets
        sheets = excel_handler.get_sheet_names()
        for sheet in sheets:
            handler = CaseInfoHandler(excel_handler.work_book, sheet)
            # login_info = handler.login_info
            for case_info in handler.case_infos:
                case_info.headers = {} if not case_info.headers else json.loads(case_info.headers)
                run_status = "yes" if case_info.run is None or case_info.run == ' ' \
                    else case_info.run
                run_status = run_status.lower()
                if run_status == 'yes':
                    # yield输出的是一个对象，相当于一个容器，想取什么数据就取什么数据
                    yield sheet, case_info, src, handler


class RequestInfo:
    def __init__(self, file, sheet, case_info, handler):
        self.http_request = HttpRequest(case_info)
        # self.work_book = ExcelHandler(file).work_book
        self.case_handler = handler
        self.case_info = case_info
        self.sheet_tokens = {}
        self.token = None
        self.file = file
        self.sheet = sheet

    def set_token(self):

        # 确保一个sheet只登录一次
        # {"file作为key":[{"sheet1":"cookie"},{"sheet2":"cookie"}]}
        self.file = self.file.split('/')[-1]

        # 如果sheet对应的token已存在则不会重新生成token
        if self.file in list(self.sheet_tokens.keys()):
            if self.sheet not in self.sheet_tokens[self.file]:
                sheet_token = {}
                # 登录获取token，并添加到字典中做标记
                self.token = self.http_request.get_token()
                sheet_token[self.sheet] = self.token
                self.sheet_tokens[self.file].append(sheet_token)

        else:
            # 将file添加到字典中，并登录获取token
            token_list = []
            token_dict = {}
            self.token = self.http_request.get_token()
            token_dict[self.sheet] = self.token
            token_list.append(token_dict)
            self.sheet_tokens[self.file] = token_list
        return self.token

    def do_request(self):
        """
        占位符填充
        执行http请求
        """

        # 填充占位符参数
        self.case_handler.parse_params(self.case_info).parse_path(self.case_info)
        # 执行请求
        # http_handler = HttpRequest(self.case_info)
        result = self.http_request.execute(self.case_handler.case_infos)
        return result


if __name__ == '__main__':
    cases = getCasesInfoFromExcel('isc-permission-service')
    for case in cases:
        print(case)
