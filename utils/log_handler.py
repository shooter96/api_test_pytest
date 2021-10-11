import logging
import os

from utils.yaml_handler import do_yaml
from utils.path_handler import LOGS_DIR


class MyLogger(object):

    @classmethod
    def create_logger(cls):
        """创建日志收集器 """
        # 创建一个日志收集器
        my_log = logging.getLogger(do_yaml.read("log", "log_name"))
        # 设置日志收集器的收集等级
        my_log.setLevel(do_yaml.read("log", "logger_level"))
        # 设置日志输出的格式
        formater = logging.Formatter(do_yaml.read("log", "formatter"))
        # 创建一个输出导控制台的日志输出渠道
        sh = logging.StreamHandler()
        sh.setLevel(do_yaml.read("log", "stream_level"))
        # 设置输出导控制台的格式
        sh.setFormatter(formater)
        # 将输出渠道添加到日志收集器中
        my_log.addHandler(sh)

        # 创建一个输出导文件的渠道
        fh = logging.FileHandler(filename=os.path.join(LOGS_DIR, do_yaml.read("log", "logfile_name")),
                                 encoding='utf8')
        fh.setLevel(do_yaml.read("log", "logfile_level"))
        # 设置输出导文件的日志格式
        fh.setFormatter(formater)
        # 将输出渠道添加到日志收集器中
        my_log.addHandler(fh)
        return my_log


do_log = MyLogger.create_logger()



