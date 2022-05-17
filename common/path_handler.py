# @author: wy
# @project:api_test_pytest
# os 是 outputstream 输出流
import os

# 获取项目根路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EXCEL_PATH = os.path.join(BASE_DIR, 'datas')


