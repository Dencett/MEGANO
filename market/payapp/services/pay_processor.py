import time
from threading import Thread, Lock
import requests
from queue import Queue


class PayThread(Thread):
    def __init__(self, queue: Queue, lock: Lock, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue_lock = lock
        self.queue: Queue = queue

    def run(self):
        if not self.queue_lock.locked():
            with self.queue_lock:
                count = 0
                while not self.queue.empty():
                    count += 1
                    order, bank_account, record = self.queue.get()
                    params = {"identify_number": order.number, "cart_number": bank_account, "price": order.price}
                    print(f"params = {params}")
                    response = requests.request("POST", url="http://127.0.0.1:8000/api/meganopay/", data=params)
                    time.sleep(2)
                    print(f"count={count} response={response.text} status={response.status_code}")
                    if response.status_code == 200:
                        self.set_status_to_order(order=order)
                    self.register_pay_response(record=record, answer_from_api=response.text)

        else:
            print(f"finish {self.name}")
            return

    def register_pay_response(self, record, answer_from_api):
        record.answer_from_api = answer_from_api
        record.save()

    def set_status_to_order(self, order):
        order.status_payed = True
        order.save()
