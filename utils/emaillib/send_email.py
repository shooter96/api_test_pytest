import smtplib
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, parseaddr
import os


def send_text_email(sender, receivers, subject, content, file=None):
    # 登录
    try:
        smtpObj = smtplib.SMTP_SSL(sender.host, sender.port, timeout=2)
        smtpObj.ehlo(sender.port)
        smtpObj.login(sender.addr, sender.password)
    except smtplib.SMTPException:
        print('登录邮箱失败')
        return
    # 收件人必须是数组
    if not isinstance(receivers, list):
        print('收件人参数类型错误，只能为数组')
        return

    # 创建一个带附件的实例
    msg = MIMEMultipart()
    # 构建附件
    # 发送的附件,列表
    report_list = file
    for report in report_list:
        # filename = report.split('/')[-1]
        # report_path = os.getcwd() + '/result/' + report
        att = MIMEApplication(open(report, 'rb').read())
        # att["Content-Type"] = 'application/octet-stream'
        # 注意：此处basename要转换为gbk编码，否则中文会有乱码
        filename = report.split('/')[-1]
        att.add_header('Content-Disposition', 'attachment', filename=('gbk', '', filename))
        msg.attach(att)

    # 处理邮件内容和发件人
    text_part = MIMEText(content, 'plain', 'utf-8')
    msg.attach(text_part)
    msg['From'] = __format_addr(u'' + sender.name + ' <%s>' % sender.addr)
    msg['Subject'] = Header(u'%s' % subject, 'utf-8').encode()

    for receiver in receivers:
        # 处理收件人，并发送
        msg['To'] = __format_addr(u'' + receiver.name + ' <%s>' % receiver.addr)
    try:
        smtpObj.sendmail(sender.addr, [receiver.addr for receiver in receivers], msg.as_string())
        smtpObj.quit()
        print('邮件发送成功')
    except smtplib.SMTPException:
        print('邮件发送失败')


def __format_addr(formatter):
    """
    将邮件的 name 转换成 utf-8 格式
    addr 如果是 unicode，则转换 utf-8 输出，否则直接输出 addr
    """
    name, addr = parseaddr(formatter)
    return formataddr((Header(name, 'utf-8').encode(), addr))


class EmailInfo:

    def __init__(self, name=None, addr=None, host=None, port=None, password=None):
        self.name = name
        self.addr = addr
        self.host = host
        self.port = port
        self.password = password
