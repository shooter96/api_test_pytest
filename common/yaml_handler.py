# @author: wy
# @project:api_test_pytest
# yaml文件读取通用方法封装
import yaml


class YamlHandler:
    def __init__(self, filename):
        try:
            # 加载
            with open(filename, mode='w', encoding='utf-8') as file:
                self.config = yaml.full_load(file)
        except Exception as e:
            # 返回异常类型，异常信息
            print(repr(e))

    def read_yaml(self, section, option):
        """
        section: 区域名
        option：选项名
        """
        return self.config[section][option]

