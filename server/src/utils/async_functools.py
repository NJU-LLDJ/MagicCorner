from collections.abc import Callable, Coroutine
from concurrent.futures import Executor, ProcessPoolExecutor, ThreadPoolExecutor
from functools import wraps
from multiprocessing import reduction
from typing import TypeVar, ParamSpec

import dill  # type: ignore

# 标准库pickle模块不支持对某些函对象的序列化，使用dill模块替代
reduction.ForkingPickler.dumps = dill.dumps  # type: ignore
reduction.ForkingPickler.loads = dill.loads  # type: ignore

_P = ParamSpec("_P")
_RT_co = TypeVar("_RT_co")
_ST_contra = TypeVar("_ST_contra")
_YT_co = TypeVar("_YT_co")


class SyncExecutor:
    """同步执行器抽象基类，用于同步执行异步函数，子类需实现run方法"""

    __slots__ = ("_pool",)

    def __init__(self, pool: Executor):
        """
        初始化同步执行器
        Args:
            pool: 线程池或进程池
        """
        self._pool = pool

    @staticmethod
    def _async_run(
        func: Callable[_P, Coroutine[_YT_co, _ST_contra, _RT_co]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> _RT_co:
        """
        作为多线程或多进程的目标函数，在新事件循环中运行异步函数，
        Args:
            func: 异步函数
            *args: func的位置参数
            **kwargs: func的关键字参数

        Returns:
            func的返回值
        """
        import asyncio  # 避免报错 NameError: name 'asyncio' is not defined

        loop = asyncio.new_event_loop()
        return loop.run_until_complete(func(*args, **kwargs))

    def run(
        self,
        func: Callable[_P, Coroutine[_YT_co, _ST_contra, _RT_co]],
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> _RT_co:
        """
        运行异步函数并同步返回结果，阻塞直至返回结果
        Args:
            func: 异步函数
            *args: func的位置参数
            **kwargs: func的关键字参数

        Returns:
            func的返回值
        """
        return self._pool.submit(self._async_run, func, *args, **kwargs).result()


process_sync_executor = SyncExecutor(ProcessPoolExecutor())


def run_process_sync(
    func: Callable[_P, Coroutine[_YT_co, _ST_contra, _RT_co]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> _RT_co:
    """
    使用进程池运行异步函数并同步返回结果，阻塞直至返回结果
    Args:
        func: 异步函数
        *args: func的位置参数
        **kwargs: func的关键字参数

    Returns:
        func的返回值
    """
    return process_sync_executor.run(func, *args, **kwargs)


def process_sync(
    func: Callable[_P, Coroutine[_YT_co, _ST_contra, _RT_co]]
) -> Callable[_P, _RT_co]:
    """
    被装饰的异步函数将在新进程中运行，阻塞直至返回结果，可被视为同步函数
    Args:
        func: 异步函数

    Returns:
        同步化的func
    """

    @wraps(func)
    def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _RT_co:
        return run_process_sync(func, *args, **kwargs)

    return wrapper


thread_sync_executor = SyncExecutor(ThreadPoolExecutor())


def run_thread_sync(
    func: Callable[_P, Coroutine[_YT_co, _ST_contra, _RT_co]],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> _RT_co:
    """
    使用线程池运行异步函数并同步返回结果，阻塞直至返回结果
    Args:
        func: 异步函数
        *args: func的位置参数
        **kwargs: func的关键字参数

    Returns:
        func的返回值
    """
    return thread_sync_executor.run(func, *args, **kwargs)


def thread_sync(
    func: Callable[_P, Coroutine[_YT_co, _ST_contra, _RT_co]]
) -> Callable[_P, _RT_co]:
    """
    被装饰的异步函数将在新线程中运行，阻塞直至返回结果，可被视为同步函数
    Args:
        func: 异步函数

    Returns:
        同步化的func
    """

    @wraps(func)
    def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _RT_co:
        return run_thread_sync(func, *args, **kwargs)

    return wrapper


sync = thread_sync  # thread_sync的开销比process_sync更小，故将其作为默认同步化装饰器
