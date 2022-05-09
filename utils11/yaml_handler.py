# -*- coding: utf-8 -*-
import yaml

from utils11.path_handler import CONFIG_FILE_PATH


class HandleYaml:
    def __init__(self, filename):
        with open(filename, encoding="utf-8") as one_file:
            self.datas = yaml.full_load(one_file)

    def read(self, section, option):
        """
        读数据
        :param section: 区域名
        :param option: 选项名
        :return:
        """
        return self.datas[section][option]

    @staticmethod
    def write(datas, filename):
        """
        写数据
        :param datas: 嵌套字典的字典
        :param filename: yaml文件路径
        :return:
        """
        with open(filename, mode="w", encoding="utf-8") as one_file:
            yaml.dump(datas, one_file, allow_unicode=True)


do_yaml = HandleYaml(CONFIG_FILE_PATH)

if __name__ == '__main__':
    # do_yaml = HandleYaml("configs/testcase.yaml")
    # do_yaml = HandleYaml(r"C:\Users\KeYou\PycharmProjects\LemonAPITest\configs\testcase.yaml")
    do_yaml = HandleYaml(CONFIG_FILE_PATH)
    # datas = {
    #     "excel": {
    #         "cases_path": "cases.xlsx",
    #         "result_col": 5
    #     },
    #     "msg": {
    #         "success_result": "通过",
    #         "fail_result": "Fail"
    #     }
    # }
    # do_yaml.write(datas, "write_datas.yaml")
    pass

