import os

import pytest

pytest.main(['testcase/test_cases.py', '--alluredir', './report/xml'])
os.system('allure generate ./report/xml -o ./report/allure-report --clean')
