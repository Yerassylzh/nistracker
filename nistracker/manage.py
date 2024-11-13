import os
import sys

from core.diary import DiaryDriver
from core.timetable import TimeTable
from core.thread_worker import WorkerThread, Task

worker_thread = WorkerThread()
diary_driver = None
tt_loader = TimeTable()

is_diary_ready = dict()

def diary_driver_init():
    global diary_driver
    diary_driver = DiaryDriver()


async def diary_driver_get_ready():
    global diary_driver
    await diary_driver.open_loginpage()


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nistracker.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    worker_thread.start()

    worker_thread.add_task(
        task=Task(
            diary_driver_init,
            args=[],
            kwargs={},
            result_dict={},  # it will be None or DiaryDriver
            asynchronous=False
        )
    )
    worker_thread.add_task(
        task=Task(
            diary_driver_get_ready,
            args=[],
            kwargs={},
            result_dict=is_diary_ready,
            asynchronous=True
        )
    )
    main()
