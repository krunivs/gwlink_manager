import datetime
import time
from threading import Thread

import threading
from copy import copy


class Consumer:
    def __init__(self):
        self._event_poll_thread_object = None
        self.queue_lock = threading.Lock()
        self.event_queue = []

    def start(self):
        self._event_poll_thread_object = \
            threading.Thread(target=self.__event_poll,
                             args=(),
                             daemon=True)
        self._event_poll_thread_object.start()

    def emit(self, event):
        self.queue_lock.acquire()
        self.event_queue.append(event)
        self.queue_lock.release()

    def pop_event(self):
        item = None
        self.queue_lock.acquire()
        if len(self.event_queue) > 0:
            item = self.event_queue.pop(0)
        self.queue_lock.release()

        return item

    def __event_poll(self):
        while True:
            event = self.pop_event()
            if event is not None:
                event_type = event['event_type']
                print('in __event_poll(), event_type = {}'.format(event_type))
                event_callback = event['event_callback']
                parameter = event['parameter']
                event_callback(parameter)

            time.sleep(1)

class Provider:
    event_template = {
        'event_type': str(),
        'event_callback': None,
        'parameter': None
    }

    def __init__(self, cons: Consumer):
        self.consumer = cons

    @staticmethod
    def hello_event_handler(param1):
        print(param1)

    def send_event(self):
        event = copy(self.event_template)
        event['event_type'] = 'hello_event'
        event['event_callback'] = self.hello_event_handler
        event['parameter'] = 'hello world!!!'
        self.consumer.emit(event)


if __name__ == "__main__":
    sample_dict = {'1':'aaa', '2':'bbb'}
    sample_dict.pop('1')

    if sample_dict:
        print('not empty')
    else:
        print('empty')

    # consumer = Consumer()
    # consumer.start()
    # provider = Provider(consumer)
    # provider.send_event()
    #
    # time.sleep(10000000)
# from redis import Redis
# from redis_dict import RedisDict
#
# if __name__ == "__main__":
#     dic = RedisDict(namespace='bar')
#
#     r = Redis()
#     data = {
#         'name': 'charls',
#         'age': 13,
#         'email':'chrl@gmail.com',
#         'budget': {
#             'kakao': 1123,
#             'nonghyup': 123123
#         }
#     }
#     dic['north_cls'] = data
#     print(dic)
#     k = r.keys()
#     print(k)
#     rdata = r.get('bar:north_cls')
#     print(rdata)
#     data2 = {
#         'age': 23,
#         'email':'chismea@gmail.com',
#         'budget': {
#             'kakao': 11231,
#             'nonghyup': 1213123
#         }
#     }
#     dic['north_cls'] = data2
#     rdata = r.get('bar:north_cls')
#     print(rdata)
#
#     # r.json().set('employee', Path.root_path(), data)
#     # rdata = r.hgetall('employee')
#     # print(rdata)
#     # r.delete('employee:1')
#     # rdata = r.hgetall('employee:1')
#     # print(rdata)
