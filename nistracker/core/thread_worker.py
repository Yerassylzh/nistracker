import threading
import queue
import asyncio


class Task:
    def __init__(self, func, args: list, kwargs: dict, result_dict: dict, asynchronous: bool):
        self.asynchronous = asynchronous
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.result = result_dict
        self.done = False


class WorkerThread:
    def __init__(self):
        self.tasks = queue.Queue()

    def _work(self):
        while True:
            task = self.tasks.get()
            print("Work")
            if task.asynchronous:
                asyncio.run(self._execute_async_task(task))
            else:
                task.result["result"] = task.func(*task.args, **task.kwargs)
            task.done = True

    async def _execute_async_task(self, task):
        task.result["result"] = await task.func(*task.args, **task.kwargs)

    def start(self):
        threading.Thread(target=self._work, daemon=True).start()

    def add_task(self, task: Task):
        assert isinstance(task, Task)
        self.tasks.put(task)
