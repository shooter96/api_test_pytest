import struct

from utils.emaillib.email_support import send_text


def str_is_none(source):
    """
    判断字符串不为空
    """
    if source == '' or source == 'NULL' or source == 'None' or source is None:
        return True
    return False


def isExcel(filename):
    """
    通过文件头判断文件的真实类型是否为 Excel
    D0CF11E0 为 .xls
    504B0304 为 。xlsx
    但是有几率误判，所以运行目录下最好不要放置其他文件
    """
    # 读取文件二进制流
    bin_file = open(filename, 'rb')
    # Excel 文件头
    excels = ['D0CF11E0', '504B0304']
    for excel in excels:
        # 读取文件头长度
        len_of_bytes = round(len(excel) / 2)
        # 每次读取都要回到文件头，不然会一直往后读取
        bin_file.seek(0)
        # 一个 "B"表示一个字节
        bin_file_header = struct.unpack_from("B" * len_of_bytes, bin_file.read(len_of_bytes))
        # 将文件头转为十六进制
        file_header = __bytes2hex(bin_file_header)
        # 是某种格式的 Excel 直接返回
        if file_header == excel:
            bin_file.close()
            return True
    bin_file.close()
    return False


def get_value(source, steps):
    """
    根据入参字典以及取值步骤取出结果

    取值步骤为 . 连接，如：datas.records.0.name 含义为取 datas 下 records 列表的第 0 条的 name 字段的值
    """
    # 分割取值步骤为列表
    keys = steps.split(".")
    try:
        # 循环取值步骤字典
        for i in range(0, len(keys)):
            # 取字段值
            key = keys[i]
            # 如果为数字则转为数字(数字代表从列表取值)，否则为字符
            key = key if not key.isdigit() else int(key)
            # 从结果字典取值
            source = source[key]
    # 出现异常直接填充为空字符
    except Exception:
        return ''
    return source


def set_value(value, target, steps):
    # 以 . 分割插入步骤为数组
    keys = steps.split(".")
    # 循环找到对应位置插入
    for i in range(0, len(keys)):
        key = keys[i]
        # 如果当前步骤为字符串类型的数字，转为 int
        key = key if not key.isdigit() else int(key)
        # 取到最后了，直接将值插入该位置
        if i == len(keys) - 1:
            target[key] = value
        # 否则继续往下找插入位置
        # 如果末尾为数字，则认为入参为[]
        elif len(keys) > 1 and (keys[len(keys) - 1]).isdigit():
            try:
                value_list = [] if not target[keys[len(keys) - 2]] else target[keys[len(keys) - 2]]
            except KeyError:
                value_list = []
            value_list.append(value)
            target[keys[len(keys) - 2]] = value_list
            break
        else:
            try:
                # 从目标中取当前 key 对应的值为下一次的目标
                target = target[key]
            except KeyError:
                # 报错则下一次目标为空字典
                target.update({key: {}})
                target = target[key]


def __bytes2hex(bin_file_header):
    """
    将二进制转为十六进制
    """
    num = len(bin_file_header)
    hex_str = u''
    for i in range(num):
        t = u'%x' % bin_file_header[i]
        if len(t) % 2:
            hex_str += u'0'
        hex_str += t
    return hex_str.upper()


def email_content(host, results, case_num, file=None):
    if not bool(results):
        content = '本次测试无可执行文件，请检查是否在 case 下放置可执行文件了'
    else:
        content = '测试结果:\n\n'
        for res in results:
            content += '用例报告文件：' + res.get('target') + '\n'
            if res.get('failed_num') == 0:
                content += '用例执行全部通过！！'
            else:
                content += '失败:' + str(res.get('failed_num')) + '\t成功:' + str(res.get('success_num')) + '\n'
                content += '存在用例执行失败的Sheet:' + '\t{}\n'.format(res.get('sheets'))
            content += '\n\n'
        content += '执行测试用例总数：' + str(case_num.get('run_total')) + '\n'
        content += '测试用例执行详情见附件！' + '\n\n'
        if host == 'http://10.30.30.31:38080':
            coverage_host = host.replace('38080', '45000')
            content += '以下是覆盖率报告链接：' + '\n'
            content += 'dmc报告: {}/report/isc-dmc-service/report/index.html'.format(coverage_host) + '\n'
            # content += 'shadow报告: http://192.168.10.34:45000/report/isc-shadow-service/report/index.html' + '\n'
            content += 'proxy报告: {}/report/isc-proxy-service/report/index.html'.format(coverage_host) + '\n'
            content += 'video报告: {}/report/isc-video-service/report/index.html'.format(coverage_host) + '\n'
            content += 'permission报告: {}/report/isc-permission-service/report/index.html'.format(coverage_host) + '\n'
    send_text(subject='接口自动化测试报告', content=content, file=file)
