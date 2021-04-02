# coding=utf-8
import yaml
import os


class HandelYaml:
    def __init__(self, filename):
        try:
            with open(filename, encoding='utf-8') as one_file:
                self.test_data = yaml.full_load(one_file)
        except FileNotFoundError as e:
            raise e

    def read(self, section, option):
        '''

        :param section:区域名
        :param option:选项名
        :return:
        '''
        return self.test_data[section][option]

    @staticmethod
    def write(test_data, filename):
        '''

        :param test_data:写入的数据，字典嵌套字典
        :param filename:yaml文件路径
        :return:
        '''
        with open(filename, mode="w", encoding='utf-8') as one_file:
            yaml.dump(test_data, one_file, allow_unicode=True)  # allow_unicode：防止中文写入乱码


if __name__ == '__main__':
    # 项目目录
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    CONFIG_DIR = os.path.join(BASE_DIR, "config")
    CONFIG_FILE_PATH = os.path.join(CONFIG_DIR, "testcase.yaml")
    print(CONFIG_FILE_PATH)

    do_yaml = HandelYaml(CONFIG_FILE_PATH)
    read_result = do_yaml.read('test_96', 'login_name')
    print(read_result)

    test_data = {
        "excel": {
            "cases_path": "cases.xlsx",
            "result_col": 5
        },
        "msg": {
            "success_result": "通过",
            "fail_result": "Fail"
        }
    }
    # 覆盖写入
    # do_yaml.write(test_data, CONFIG_FILE_PATH)
