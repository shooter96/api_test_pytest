# @author: wy
# @project:api_test_pytest
def get_value(source, step):
    '''
    source: 依赖的的实际内容 {}
    setp: 取值的步骤
    '''

    step_list = str(step).split('.')
    for key in step_list:
        try:
            # 如果为数字则转为数字(数字代表从列表取值)，否则为字符
            # isdigit() 方法检测字符串是否只由数字组成。
            key = key if not key.isdigit() else int(key)
            source = source[key]
        except Exception as e:
            return " "

    return source

