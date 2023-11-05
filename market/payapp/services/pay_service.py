from queue import Queue
from threading import Lock
from django.conf import settings

from payapp.services.pay_processor import PayThread
from payapp.models import OrderPayStatus
from orders.models import Order


def pay_order(order: Order, bank_account: int, host_name: str) -> None:
    pay_queue: Queue = settings.PAY_QUEUE
    lock: Lock = settings.PAY_QUEUE_LOCK
    pay_url = settings.PAY_URL
    url = "http://" + host_name + pay_url
    record = OrderPayStatus(order=order)
    record.save()
    task = (order, bank_account, record)
    order.status = Order.STATUS_NOT_PAID
    order.save()
    pay_queue.put(task, block=True)
    PayThread(pay_queue, lock, url).start()
