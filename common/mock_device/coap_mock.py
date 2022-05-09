import hashlib
import json
import random
import time
from threading import Thread
from coapthon import defines
from coapthon.client.helperclient import HelperClient
from coapthon.messages.request import Request
from queue import Queue
from framework.common.BaseConfig import BaseConfig


# todo：模拟驱动配置信息读取
class CoapMock():

    def __init__(self):
        self.q = Queue()
        self.qq = Queue()
        bc = BaseConfig.get_common_config()
        self.pk = bc.get("mock_device", "coap_pk")
        self.dev_id = bc.get("mock_device", "coap_dev_id")
        self.secret = bc.get("mock_device", "coap_secret")
        self.port = int(bc.get("mock_device", "coap_port"))
        self.host = bc.get("environment", "domain").split(":")[0]
        self.user = self.pk + '@' + self.dev_id
        self.passwd = self.pk + self.dev_id + self.secret
        self.password = hashlib.sha256(self.passwd.encode('utf-8')).hexdigest()
        self.client_id = self.pk + '@' + self.dev_id
        self.up = '/mqtt/up/dev/{}/{}?c={}&u={}&p={}'.format(self.pk, self.dev_id, self.client_id, self.user,
                                                             self.password)
        self.down = '/mqtt/down/dev/{}/{}?c={}&u={}&p={}'.format(self.pk, self.dev_id, self.client_id, self.user,
                                                                 self.password)
        self.stop = False

    # 上报
    def push_data(self):
        client = HelperClient(server=(self.host, self.port))
        n = 0
        params = ''
        while not self.stop:
            timestamp = int(time.time() * 1000)
            raw_data = {
                "operate": "ATTR_UP",
                "operateId": 1,
                "data": [{
                    "pk": self.pk,
                    "devId": self.dev_id,
                    "time": timestamp,
                    "params": {'temperature': n, 'humidity': random.randint(0, 100)}}]
            }
            lowPower_data = {
                "operate": "EVENT_UP",
                "operateId": 1,
                "data": [{
                    "pk": self.pk,
                    "devId": self.dev_id,
                    "identifier": "lowPower",
                    "time": timestamp,
                    "params": {'temperature': n, 'humidity': random.randint(0, 100)}}]
            }
            data = get_que_data(self.qq)
            try:
                p = data['data']['params']['temperature']
                if p:
                    n = p
            except:
                pass

            n = n + 10
            if n > 99:
                n = 0
            if n < 30:
                # lowPower_data.get('data')[0].get('params').update(params)
                data = lowPower_data
            else:
                # raw_data.get('data')[0].get('params').update(params)
                data = raw_data
            print('上报数据为{}'.format(data))
            data = json.dumps(raw_data, ensure_ascii=False, sort_keys=False)
            response = client.put(self.up, data, timeout=3)
            time.sleep(3)

    # 订阅
    def subscribe_data(self):
        client = HelperClient(server=(self.host, self.port))
        request = Request()
        request.code = defines.Codes.GET.number
        request.type = defines.Types['NON']
        request.destination = (self.host, self.port)
        request.uri_path = self.down
        request.observe = 0
        request.content_type = defines.Content_types["application/json"]
        # request.payload = '<value>"+str(payload)+"</value>'
        while not self.stop:
            response = client.send_request(request, timeout=10)
            data = response.payload
            if data:
                json_data = json.loads(data.decode())
                a = json_data.copy()
                self.qq.put(a)
                self.q.put(json_data)

    # 上报温度属性回应
    def attr_write_res(self):
        client = HelperClient(server=(self.host, self.port))
        while not self.stop:
            json_data = get_que_data(self.q)
            timestamp = int(time.time() * 1000)
            try:
                temperature = json_data.get('data').get('params').get('temperature')
            except:
                pass
            else:
                if temperature:
                    data = {
                        "operate": "ATTR_WRITE_RES",
                        "operateId": 1,
                        "data": {
                            "pk": self.pk,
                            "devId": self.dev_id,
                            "time": timestamp,
                            "params": {
                                "temperature": "{}".format(temperature),
                            }
                        },
                        "code": 0
                    }
                    data = json.dumps(data, ensure_ascii=False, sort_keys=False)
                    response = client.put(self.up, data)

    def do_mock(self):
        t1 = Thread(target=self.attr_write_res)
        t2 = Thread(target=self.push_data)
        t3 = Thread(target=self.subscribe_data)
        t1.start()
        t2.start()
        t3.start()

    def stop_mock(self):
        self.stop = True


def get_que_data(que: Queue):
    try:
        time.sleep(0.1)
        data = que.get_nowait()
    except:
        pass
    else:
        return data


if __name__ == '__main__':
    cm = CoapMock()
    cm.do_mock()
    # t1 = Thread(target=cm.attr_write_res)
    # t2 = Thread(target=cm.push_data)
    # t3 = Thread(target=cm.subscribe_data)
    # t1.start()
    # t2.start()
    # t3.start()
    time.sleep(10)
    cm.stop_mock()
    print("asd")
