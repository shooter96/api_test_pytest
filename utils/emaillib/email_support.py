import os
import platform
import yaml

from utils.emaillib.send_email import send_text_email, EmailInfo

"""
还应该提供
HTML、图片、附件
图片、附件应当传入路径
"""


def send_text(subject, content, file=None):
    try:
        config_name = 'emaillib.yml'
        linking = '\\' if platform.system() == 'Windows' else '/'
        config = open(config_name, encoding='utf-8') if os.path.exists(config_name) \
            else open(os.path.dirname(os.path.abspath(__file__)) + linking + config_name, encoding='utf-8')
        config = yaml.full_load(config)
    except Exception:
        raise RuntimeError('请检查 emaillib.yml 是否存在，或格式是否正确')
    sender = config['sender']
    receiverConf = config['receiver']
    names = receiverConf['name']
    addrs = receiverConf['addr']
    receivers = [EmailInfo(name=reciever[0], addr=reciever[1]) for reciever in list(zip(names, addrs))]
    send_text_email(sender=EmailInfo(name=sender['name'], addr=sender['addr'], host=sender['host'], port=sender['port'],
                                     password=sender['password']), receivers=receivers, subject=subject,
                    content=content, file=file)
