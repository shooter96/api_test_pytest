import os
import time

from utils11.excel_handler import CaseInfoHolder, ExcelParser
from utils11.common_handler import isExcel
from utils11.yaml_handler import do_yaml


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
        # 同一个datas目录下用例的sheetname要唯一
        if sheet_name in sheet_names:
            holder = CaseInfoHolder(src_parser.work_book, sheet_name, host)
            for case_info in holder.case_infos:
                step = case_info.step
                step_list.append(step)
            return holder, step_list
        else:
            count = count + 1


def pytest_addoption(parser):
    parser.addoption(
        "--sheet",
        action="append",
        default=[],
        help="list of sheet to pass to test11 functions",
    )


def pytest_generate_tests(metafunc):
    params = []
    ids = []
    for sheet in metafunc.config.getoption('sheet'):
        holder, step_list = init_case(sheet)
        ids.extend(step_list)
        for case_info in holder.case_infos:
            param = [case_info, holder, sheet]
            params.append(param)
    metafunc.parametrize('case_info,holder,sheet', params, ids=ids)


def pytest_collection_modifyitems(items):
    """
    测试用例收集完成时，将收集到的item的name和nodeid的中文显示在控制台上
    :return:
    """
    for item in items:
        item.name = item.name.encode("utf-8").decode("unicode_escape")
        item._nodeid = item.nodeid.encode("utf-8").decode("unicode_escape")
        print(item.nodeid)
