import struct
from paho.mqtt.client import Client
import json
import hashlib
import time
import random
from framework.common.BaseConfig import BaseConfig
from threading import Thread


# todo：模拟驱动配置信息读取
class MqttMock():
    def __init__(self):
        bc = BaseConfig.get_common_config()
        self.host = bc.get("environment", "domain").split(":")[0]
        self.port = int(bc.get("mock_device", "mqtt_port"))
        self.temperature = int(bc.get("mock_device", "mqtt_temperature"))
        self.humidity = int(bc.get("mock_device", "mqtt_humidity"))
        self.step = int(bc.get("mock_device", "mqtt_step"))
        self.interval = int(bc.get("mock_device", "mqtt_interval"))
        self.protocol = bc.get("mock_device", "mqtt_protocol")
        self.pk = bc.get("mock_device", "mqtt_pk")
        self.dev_id = bc.get("mock_device", "mqtt_dev_id")
        self.secret = bc.get("mock_device", "mqtt_secret")
        self.if_reconnect = bc.get("mock_device", "mqtt_reconnect")
        self.passwd = self.pk + self.dev_id + self.secret
        self.user = self.pk + '@' + self.dev_id
        self.sha256_passwd = hashlib.sha256(self.passwd.encode('utf-8')).hexdigest()
        self.postfix = self.pk + '/{}'.format(self.dev_id)
        self.down = 'down/dev/' + self.postfix
        self.up = 'up/dev/' + self.postfix
        self.flag = 0
        self.stop = False

    def on_connect(self, client, userdata, flags, rc):
        print('mqtt connected')
        client.subscribe([(self.down, 0)])

    def on_message(self, client, userdata, msg):
        print('收到消息 {}: {}'.format(msg.topic, msg.payload))
        pl = msg.payload
        global temperature
        try:
            data = json.loads(pl)
            operate = data.get('operate')
            if operate == 'ATTR_WRITE':
                temperature = data.get("data").get("params").get("temperature") + 10
                data['code'] = 0
                data['operate'] = 'ATTR_WRITE_RES'
                client.publish(self.up, json.dumps(data))

                print('属性下发回应:{}'.format(data))
            if operate == 'SERVICE_DOWN':
                temperature += 2
                data['code'] = 0
                data['operate'] = 'SERVICE_DOWN_RES'
                client.publish(self.up, json.dumps(data))
                print('服务下发回应:{}'.format(data))
        except Exception:
            tup, hex_msg = self.byte_to_hex(pl)
            if tup[2] == 3:
                temperature = tup[-1] + 10
            if tup[2] == 4:
                temperature += 2

    def byte_to_hex(self, b):
        if len(b) == 19:
            tup = struct.unpack("!qqbbb", b)
            m_id = '{:016x}'.format(tup[0])
            m_time = m_id
            m_type = '0{}'.format(tup[2])
            m_temp = '{:02x}'.format(tup[3])
            m_hum = '{:02x}'.format(tup[4])
            return tup, m_id + m_time + m_type + m_temp + m_hum
        else:
            tup = struct.unpack("!qqb{}b".format(len(b) - 17), b)
            m_id = '{:016x}'.format(tup[0])
            m_time = m_id
            m_type = '0{}'.format(tup[2])
            return tup, m_id + m_time + m_type + hex(tup[3])

    def on_disconnect(self, client, userdata, rc):
        if self.if_reconnect == "True":
            client.reconnect()
        else:
            print("mqtt断开连接")

    def push_data(self):

        client = Client(client_id=self.user, clean_session=False)
        client.username_pw_set(self.user, self.sha256_passwd)

        client.on_connect = self.on_connect
        client.on_message = self.on_message

        client.connect(self.host, self.port)
        client.loop_start()

        # if cfg.has_section("data"):
        #     payload = json.loads(cfg.get("data", "payload"))
        #     while True:
        #         client.publish(up, json.dumps(payload))
        #         print('属性上报:{}'.format(payload))
        #         time.sleep(interval)
        if self.protocol.lower() == 'ilink':
            while not self.stop:
                payload = {"operate": "ATTR_UP", "operateId": 1, "data": [
                    {"pk": self.pk, "devId": self.dev_id, "time": int(time.time() * 1000),
                     "params": {"temperature": self.temperature, "humidity": self.humidity}}]}

                # payload = {"operate": "11ATTR_UP", "operateId": 1, "data": [
                #     {"pk": pk, "devId": dev_id, "identifier": "attr-1", "time": int(time.time() * 1000),
                #      "params": {"temperature": temperature, "humidity": humidity}}]}

                client.publish(self.up, json.dumps(payload))
                print('属性上报:{}'.format(payload))
                if self.temperature < 30 and self.flag == 1:
                    event = {"operate": "EVENT_UP", "operateId": 1, "data": [
                        {"pk": self.pk, "devId": self.dev_id, "identifier": 'lowPower', "time": int(time.time() * 1000),
                         "params": {"temperature": self.temperature}}]}
                    client.publish(self.up, json.dumps(event))
                    print('事件上报:{}'.format(event))
                self.temperature += self.step
                self.humidity = random.randint(0, 100)
                if self.temperature > 100:
                    self.temperature = 0
                self.flag = 1
                time.sleep(self.interval)
        elif self.protocol.lower() == 'custom':
            while not self.stop:
                t = int(time.time() * 1000)
                msg_id = struct.pack(">q", t)
                msg_time = msg_id
                msg_type = struct.pack(">b", 1)
                temp = struct.pack(">b", self.temperature)
                hum = struct.pack(">b", self.humidity)
                message = msg_id + msg_time + msg_type + temp + hum
                client.publish(self.up, message)
                print("属性上报:{}".format(self.byte_to_hex(message)[1]))
                if self.temperature < 30 and self.flag == 1:
                    event_t = int(time.time() * 1000)
                    event_id = struct.pack(">q", event_t)
                    event_time = event_id
                    event_type = struct.pack(">b", 2)
                    event_name = 'lowPower'
                    event = event_id + event_time + event_type + event_name.encode()
                    client.publish(self.up, event)
                    print('事件上报:{}'.format(self.byte_to_hex(event)[1]))
                self.temperature += self.step
                self.humidity = random.randint(0, 100)
                if self.temperature > 100:
                    self.temperature = 0
                self.flag = 1
                time.sleep(self.interval)

    def do_mock(self):
        t1 = Thread(target=self.push_data)
        t1.start()
        print("asd")

    def stop_mock(self):
        self.stop = True


if __name__ == '__main__':
    mqttm = MqttMock()
    mqttm.do_mock()
    time.sleep(10)
    mqttm.stop_mock()
