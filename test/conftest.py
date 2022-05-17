# @author: wy
# @project:api_test_pytest
# 启动模拟器，fixture定义
from common.excel_handler import *
import pytest
import requests

def pytest_collection_modifyitems(items):
    """
    测试用例收集完成时，将收集到的name和nodeid的中文显示在控制台上
    """
    for i in items:
        i.name=i.name.encode("utf-8").decode("unicode_escape")
        print(i.nodeid)
        i._nodeid=i.nodeid.encode("utf-8").decode("unicode_escape")





