# @author: wy
# @project:api_test_pytest
import json

import pytest
import allure
import logging

from common.get_excel_case import *


@allure.epic("执行excel表格内用例")
class TestExcelCases:
    # 登录获取token、填充占位符参数、执行请求、断言（取执行结果passed断言，非passed则为执行不通过）
    str_ids = ["{}_{}".format(j.description, j.step) for i, j, k, m in
               getCasesInfoFromExcel(service_name='isc-permission-service')]

    @pytest.mark.parametrize('sheet,case_info,src,handler',
                             getCasesInfoFromExcel(service_name='isc-permission-service'),
                             ids=str_ids)
    def test_excel_cases_permission(self, sheet, case_info, src, handler):
        request_handler = RequestInfo(src, sheet, case_info, handler)  # 查看headers

        # 登录填充token
        token = RequestInfo(src, sheet, handler.login_info, handler).set_token()
        case_info.headers.update({'token': token})
        # 执行请求
        result = request_handler.do_request()
        try:
            print("入参:{}".format(case_info.params))
            print('')
            print("出参:{}".format(result))
        except Exception as e:
            raise e

        if case_info.status == "passed":
            assert True
        else:
            assert False


if __name__ == '__main__':
    pytest.main(['-s', 'test_excel.py'])
