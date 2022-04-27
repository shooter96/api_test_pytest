import os

import pytest

pytest.main(['testcase/test_cases.py', '--sheet=消息中心', '--sheet=组织架构(OpenAPI)', '--alluredir', './report/xml'])
# pytest.main(['testcase/test_cases1.py', '--sheet=组织架构(OpenAPI)','--alluredir', './report/xml'])
os.system('allure generate ./report/xml -o ./report/allure-report --clean')
