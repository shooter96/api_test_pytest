# @author: wy
# @project:api_test_pytest
import pytest

from common.excel_handler import CaseInfoHandler, ExcelHandler
import requests


class TestExcelCases:
    @classmethod
    def setup_class(cls):
        work_book = ExcelHandler('../datas/isc-permission-service/多租户-权限管理.xlsx').work_book
        sheet = '默认租户管理员'
        login_info = CaseInfoHandler(work_book, sheet).build_login_info()
        cls.params = login_info.params
        cls.login_response = requests.post(url=login_info.url, json=eval(login_info.params), headers=login_info.header)
        print(cls.login_response)

    # 登录获取token、填充占位符参数、执行请求、断言（取执行结果passed断言，非passed则为执行不通过）

    @pytest.mark.parametrize('holder,sheet_name,case_info', '调用方法,获取sheet以及case', ids=[])
    def test_excel_cases(self, holder, sheet_name, case_info):
        # 先登录
        # 再执行请求
        # allure报告
        print(self.params)
        print(self.login_response.json())
        assert 1 == 1


if __name__ == '__main__':
    pytest.main(['-s', 'test_excel.py'])
