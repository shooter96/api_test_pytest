import json
import os
import shutil
import time
import json

import pytest
from utils.yaml_handler import do_yaml
from utils.log_handler import MyLogger
from utils.excel_handler import ExcelParser, CaseInfoHolder, ExcelWriter
from utils.http_handler import HttpHandler
from utils.test_utils import isExcel, str_is_none

from utils.path_handler import PERMISSION_LOGS_DIR


def init_case(sheet_name):
    host = 'http://' + str(do_yaml.read('test_env', 'host')) + ":" + str(do_yaml.read('test_env', 'port'))
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(BASE_DIR, 'datas')
    # 加载该目录下所有文件
    file_list = os.listdir(data_path)
    file_list.sort()
    m = len(file_list)
    if m == 0:
        print("datas目录下不存在用例")
    # 目录下文件数记录
    count = 0
    # 执行文件数记录
    execute_count = 0
    result_list = []
    result_dict = {}
    # 循环文件执行测试
    dest_filename = None
    report_list = []
    sheet_run_total = 0
    holder = None
    while count < m:
        failed_sheet_name = []
        sheet_total_failed = 0
        case_total = 0
        not_run = 0
        # 得到当前文件名
        file_name = file_list[count]
        count += 1
        flag = file_name[0]
        # 过滤隐藏文件和打开时生成的临时文件
        if flag == '.' or flag == '~':
            continue
        src = os.path.join(data_path, file_name)
        # 不是 Excel 文件忽略
        if not isExcel(src):
            continue
        execute_count += 1
        print('加载第', execute_count, '个用例文件: ----->', os.path.abspath(src), flush=True)
        # 目标文件名
        dest_filename = os.path.splitext(file_name)[0] + time.strftime("_Report_%Y.%m.%d.%H.%M.%S") + \
                        os.path.splitext(file_name)[1]

        # 目标文件夹
        result_dir = "result"
        if not os.path.isdir(result_dir):
            os.mkdir(result_dir)
        # 保存，将运行完成的结果文件存在同级目录的 result 文件夹里面
        # target = os.path.join("result", os.path.split(dest_filename)[1])
        # # 复制文件
        # shutil.copyfile(src, target)
        # 打开源 Excel 工作簿
        src_parser = ExcelParser(src)
        # 打开目标 Excel 工作簿
        # target_parser = ExcelParser(target)
        # 得到所有 sheet 页
        sheet_names = src_parser.get_sheet_names()
        step_list = []

        if sheet_name in sheet_names:
            holder = CaseInfoHolder(src_parser.work_book, sheet_name, host)
            for case_info in holder.case_infos:
                step = case_info.step
                step_list.append(step)

        return holder, step_list


class TestRentalCase:
    holder, step_list = init_case("组织架构(OpenAPI)")
    cookie = HttpHandler(holder.login_info).get_cookie()

    @pytest.mark.parametrize("case_info", holder.case_infos, ids=step_list)
    def test_rental(self, case_info):

        # 填充登陆信息的 token
        case_info.headers = {} if str_is_none(case_info.headers) else json.loads(case_info.headers)
        if self.cookie:
            case_info.headers.update({'Cookie': self.cookie})
        # 填充占位符参数
        self.holder.parse_param(case_info).parse_path(case_info)
        handler = HttpHandler(case_info)
        # 执行请求

        # 判断用例是否需要执行
        if case_info.run == 'no':
            case_info.status = 'skip'
        else:
            result, compare_data, params = handler.execute(self.holder.case_infos)
            # ascii转中文
            do_log = MyLogger.create_logger(PERMISSION_LOGS_DIR)
            do_log.info("入参：{}".format(json.dumps(params).encode().decode('unicode_escape')))
            do_log.info("接口返回：{}".format(result) + "\n")
            # 该断言方式-断言失败后仍继续执行后面的代码
            pytest.assume(compare_data[0] == compare_data[1])
            # assert compare_data[0] == compare_data[1]

    holder, step_list = init_case("功能数据权限模块")

    @pytest.mark.parametrize("case_info", holder.case_infos, ids=step_list)
    def test_application(self, case_info):

        # 填充登陆信息的 token
        case_info.headers = {} if str_is_none(case_info.headers) else json.loads(case_info.headers)
        if self.cookie:
            case_info.headers.update({'Cookie': self.cookie})
        # 填充占位符参数
        self.holder.parse_param(case_info).parse_path(case_info)
        handler = HttpHandler(case_info)
        # 执行请求

        # 判断用例是否需要执行
        if case_info.run == 'no':
            case_info.status = 'skip'
        else:
            result, compare_data, params = handler.execute(self.holder.case_infos)
            # ascii转中文
            do_log = MyLogger.create_logger(PERMISSION_LOGS_DIR)
            do_log.info("入参：{}".format(json.dumps(params).encode().decode('unicode_escape')))
            do_log.info("接口返回：{}".format(result) + "\n")
            # 该断言方式-断言失败后仍继续执行后面的代码
            pytest.assume(compare_data[0] == compare_data[1])
            # assert compare_data[0] == compare_data[1]


if __name__ == '__main__':
    pytest.main()
