思路：
1、用例执行：
·根据服务去执行用例
·指定版本去构建对应的服务用例（支持多个）
·执行版本去构建所有的用例
·执行excel用例和脚本编写的用例

2、测试报告既有excel又兼容allure，可通过配置修改发送的报告形式，默认是excel

3、依赖值处理优化（减轻用例维护的难度）

4、丰富断言，支持pytest的断言方式