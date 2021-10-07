# @author: wy
# @project:api_test_pytest
import json
import os
import time
from utils.excel_handler import ExcelParser, CaseInfoHolder, ExcelWriter
from utils.http_handler import HttpHandler
from utils.test_utils import str_is_none
from utils.test_utils import isExcel
# from emaillib.email_support import send_text
import shutil
import sys
import pytest


# def email_content(host, results, case_num, file=None):
#     if not bool(results):
#         content = '本次测试无可执行文件，请检查是否在 case 下放置可执行文件了'
#     else:
#         content = '测试结果:\n\n'
#         for res in results:
#             content += '用例报告文件：' + res.get('target') + '\n'
#             if res.get('failed_num') == 0:
#                 content += '用例执行全部通过！！'
#             else:
#                 content += '失败:' + str(res.get('failed_num')) + '\t成功:' + str(res.get('success_num')) + '\n'
#                 content += '存在用例执行失败的Sheet:' + '\t{}\n'.format(res.get('sheets'))
#             content += '\n\n'
#         content += '执行测试用例总数：' + str(case_num.get('run_total')) + '\n'
#         content += '测试用例执行详情见附件！' + '\n\n'
#         if host == 'http://10.30.30.31:38080':
#             coverage_host = host.replace('38080', '45000')
#             content += '以下是覆盖率报告链接：' + '\n'
#             content += 'dmc报告: {}/report/isc-dmc-service/report/index.html'.format(coverage_host) + '\n'
#             # content += 'shadow报告: http://192.168.10.34:45000/report/isc-shadow-service/report/index.html' + '\n'
#             content += 'proxy报告: {}/report/isc-proxy-service/report/index.html'.format(coverage_host) + '\n'
#             content += 'video报告: {}/report/isc-video-service/report/index.html'.format(coverage_host) + '\n'
#             content += 'permission报告: {}/report/isc-permission-service/report/index.html'.format(coverage_host) + '\n'
#     send_text(subject='接口自动化测试报告', content=content, file=file)


if __name__ == '__main__':
    send = 0
    # 加载该目录下所有文件
    file_list = os.listdir(r'case')
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
        src = os.path.join("case", file_name)
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
            holder = CaseInfoHolder(src_parser.work_book, sheet_name, sys.argv)
            print('sheetName:[{}]'.format(sheet_name))
            cookie = HttpHandler(holder.login_info).get_cookie()
            # if sheet_name == "设备":
            #     for case_info in holder.case_infos:
            #         # 填充默认 host
            #         if str_is_none(case_info.host):
            #             case_info.host = holder.default_host
            #         # 填充登陆信息的 token
            #         case_info.headers = {} if str_is_none(case_info.headers) else json.loads(case_info.headers)
            #         if cookie:
            #             case_info.headers.update({'Cookie': cookie})
            #         # 填充占位符参数
            #         holder.parse_param(case_info).parse_path(case_info)
            #         handler = HttpHandler(case_info)
            #         # 执行请求
            #         handler.execute(holder.case_infos)
            for case_info in holder.case_infos:
                # 填充登陆信息的 token
                case_info.headers = {} if str_is_none(case_info.headers) else json.loads(case_info.headers)
                if cookie:
                    case_info.headers.update({'Cookie': cookie})
                # 填充占位符参数
                holder.parse_param(case_info).parse_path(case_info)
                handler = HttpHandler(case_info)
                # 执行请求
                handler.execute(holder.case_infos)
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

        # if 'send_email' in os.environ:
        #     if os.environ['send_email'] == "否":
        #         print('不发送邮件')
        #         send = 1
        #     else:
        #         send = 0
        # if send == 0:
        #     email_content(holder.default_host, result_list, result_dict, report_list)
