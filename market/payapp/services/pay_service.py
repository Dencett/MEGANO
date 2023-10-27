from queue import Queue
from threading import Lock
from django.conf import settings

from payapp.services.pay_processor import PayThread
from payapp.models import OrderPayStatus, TestOrder


def pay_order(order: TestOrder, bank_account: int) -> None:
    pay_queue: Queue = settings.PAY_QUEUE
    lock: Lock = settings.PAY_QUEUE_LOCK
    record = OrderPayStatus(order=order)
    record.save()
    task = (order, bank_account, record)
    pay_queue.put(task, block=True)
    PayThread(pay_queue, lock).start()
