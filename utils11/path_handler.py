# -*- coding: utf-8 -*-
import os

# one_path = os.path.abspath(__file__)
# two_path = os.path.dirname(one_path)
# three_path = os.path.dirname(two_path)
# 项目根路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 获取配置文件所在的路径
CONFIGS_DIR = os.path.join(BASE_DIR, 'conf')

# 获取配置文件所在的路径
CONFIG_FILE_PATH = os.path.join(CONFIGS_DIR, 'test_config.yml')

# 获取日志文件所在的目录路径
PERMISSION_LOGS_DIR = os.path.join(BASE_DIR, 'test11/isc-isc-permission-service-service/logs')

# 获取报告文件所在的目录路径
REPORTS_DIR = os.path.join(BASE_DIR, 'report')

