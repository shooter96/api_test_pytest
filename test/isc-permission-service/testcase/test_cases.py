import json
import os
import shutil
import time
import json

import pytest
from utils.yaml_handler import do_yaml
from utils.log_handler import do_log
from utils.excel_handler import ExcelParser, CaseInfoHolder, ExcelWriter
from utils.http_handler import HttpHandler
from utils.test_utils import isExcel, str_is_none, email_content


class TestPermissionCase:
    host = 'http://' + str(do_yaml.read('test_env', 'host')) + ":" + str(do_yaml.read('test_env', 'port'))

    def test_permission(self):
        send = 0
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_path = os.path.join(BASE_DIR, 'datas')
        # 加载该目录下所有文件
        file_list = os.listdir(data_path)
        file_list.sort()
        m = len(file_list)
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
            sheet_name = None
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
            target = os.path.join("result", os.path.split(dest_filename)[1])
            # 复制文件
            shutil.copyfile(src, target)
            # 打开源 Excel 工作簿
            src_parser = ExcelParser(src)
            # 打开目标 Excel 工作簿
            target_parser = ExcelParser(target)
            # 得到所有 sheet 页
            sheet_names = src_parser.get_sheet_names()
            # 循环 sheet 页
            for sheet_name in sheet_names:
                holder = CaseInfoHolder(src_parser.work_book, sheet_name, self.host)
                print('sheetName:[{}]'.format(sheet_name))
                cookie = HttpHandler(holder.login_info).get_cookie()
                for case_info in holder.case_infos:
                    # 填充登陆信息的 token
                    case_info.headers = {} if str_is_none(case_info.headers) else json.loads(case_info.headers)
                    if cookie:
                        case_info.headers.update({'Cookie': cookie})
                    # 填充占位符参数
                    holder.parse_param(case_info).parse_path(case_info)
                    handler = HttpHandler(case_info)
                    # 执行请求

                    # 判断用例是否需要执行
                    if case_info.run == 'no':
                        case_info.status = 'skip'
                    else:
                        result, compare_data, params = handler.execute(holder.case_infos)
                        # ascii转中文
                        do_log.info("入参：{}".format(json.dumps(params).encode().decode('unicode_escape')))
                        do_log.info("接口返回：{}".format(result) + "\n")
                        # 该断言方式-断言失败后仍继续执行后面的代码
                        pytest.assume(compare_data[0] == compare_data[1])
                        # assert compare_data[0] == compare_data[1]

                # 写 Excel 目标文件
                writer = ExcelWriter(target, target_parser.work_book, target_parser.work_book[sheet_name])
                writer.write(holder.case_infos, holder.login_info, holder.default_host)
                # 统计请求结果
                sheet_total_failed += len([ci for ci in holder.case_infos if getattr(ci, 'status') == 'failed'])
                if len([ci for ci in holder.case_infos if getattr(ci, 'status') == 'failed']) != 0:
                    failed_sheet_name.append(sheet_name)
                    print("存在用例执行失败的表单：{}".format(failed_sheet_name))

                not_run += len([ci for ci in holder.case_infos if getattr(ci, 'status') == '未执行'])
                case_total += len(holder.case_infos)
                # 记录存在错误的sheetName
            result = {'target': dest_filename}
            result.update({'total': case_total})
            if sheet_total_failed == 0:
                # result_dic[file_name] = (case_total, 0)
                result.update({'failed_num': 0})
                print('All auto test has finished, congratulations!')
            else:
                result.update({'failed_num': sheet_total_failed})
                result.update({'success_num': case_total - (sheet_total_failed + not_run)})
                result.update({'ignored': not_run})
                result.update({'sheets': failed_sheet_name})
                # result_dic[file_name] = (case_total - (sheet_total_failed + not_run), sheet_total_failed, failed_sheet_name)
                print('\033[37;41mAll auto test has finished, But failed: ' + str(
                    sheet_total_failed) + ' ,未执行:' + str(not_run) + '\033[0m')
            # 统计每个文件执行的用例数量
            sheet_run_total += case_total - not_run
            result_list.append(result)
            print('保存第', execute_count, '个结果文件: ----->', os.path.abspath(target), flush=True)
            report_list.append(target)

        else:
            print('----------- [本次 Python 自动化测试运行完毕] -----------')
            if execute_count > 0:
                print('共执行', execute_count, '个文件请在同级目录 result 下查看结果', flush=True)
                result_dict.update({"run_total": sheet_run_total})

            else:
                print('本次测试无可执行文件，请检查是否在 case 下放置可执行文件了')
            # email_content(result_dic, file=os.getcwd() + '/result/' + dest_filename)
            # email_content(holder.default_host, result_list, result_dict, report_list)

            if 'send_email' in os.environ:
                if os.environ['send_email'] == "否":
                    print('不发送邮件')
                    send = 1
                else:
                    send = 0
            if send == 0:
                email_content(holder.default_host, result_list, result_dict, 'isc-permission-service', report_list)


if __name__ == '__main__':
    pytest.main()
