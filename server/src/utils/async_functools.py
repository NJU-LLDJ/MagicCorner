import functools
import pickle
from abc import ABC, abstractmethod
from collections.abc import Callable, Coroutine
from concurrent.futures import Future, ProcessPoolExecutor, ThreadPoolExecutor
from typing import TypeVar, ParamSpec
from multiprocessing import reduction

import dill

from utils.singleton import singleton

# 标准库pickle模块不支持对某些函对象的序列化，使用dill模块替代
reduction.ForkingPickler.dumps = dill.dumps
reduction.ForkingPickler.loads = dill.loads

_YT = TypeVar("_YT")
_ST = TypeVar("_ST")
_T = TypeVar("_T")
_P = ParamSpec("_P")


class SyncExecutor(ABC):
    """同步执行器抽象基类，用于同步执行异步函数，子类需实现run方法"""

    __slots__ = ()
    _pickle_module = pickle

    @classmethod
    def set_pickle_module(cls, module):
        """设置pickle模块，用于序列化函数对象"""
        if not hasattr(module, "loads") or not hasattr(module, "dumps"):
            raise TypeError("module must have loads and dumps methods")
        cls._pickle_module = module

    @staticmethod
    def _async_run(
        func: Callable[_P, Coroutine[_YT, _ST, _T]] | bytes,
        *args: _P.args,
        **kwargs: _P.kwargs
    ):
        """作为多线程或多进程的目标函数，在新事件循环中运行异步函数，func可以是函数对象或序列化后的bytes"""
        import asyncio  # 避免在子进程中报错 NameError: name 'asyncio' is not defined

        loop = asyncio.new_event_loop()
        if isinstance(func, bytes):
            func = SyncExecutor._pickle_module.loads(func)
        return loop.run_until_complete(func(*args, **kwargs))

    @abstractmethod
    def run(
        self,
        func: Callable[_P, Coroutine[_YT, _ST, _T]],
        *args: _P.args,
        **kwargs: _P.kwargs
    ) -> _T:
        """子类需实现本方法，用_async_run运行异步函数，阻塞直至返回结果"""


@singleton
class ProcessSyncExecutor(SyncExecutor):
    """同步执行器，异步任务运行于进程池内，单例"""

    __slots__ = ("_pool",)
    _pickle_module = dill

    def __init__(self, processes: int | None = None):
        """
        初始化进程池
        Args:
            processes: 进程数，默认为os.cpu_count() or 1
        """
        # self._pool = Pool(processes)
        self._pool = ProcessPoolExecutor(processes)

    def run(
        self,
        func: Callable[_P, Coroutine[_YT, _ST, _T]],
        *args: _P.args,
        **kwargs: _P.kwargs
    ) -> _T:
        """
        运行异步函数并同步返回结果，阻塞直至返回结果
        Args:
            func: 异步函数
            *args: func的位置参数
            **kwargs: func的关键字参数

        Returns:
            func的返回值
        """
        # result = self._pool.apply_async(
        #     func=self._pickle_module.dumps(self._async_run),
        #     args=(func, *args),
        #     kwds=kwargs,
        # )
        # result.wait()
        # return result.get()
        fut: Future[_T] = self._pool.submit(self._async_run, *(func, *args), **kwargs)
        return fut.result()


@singleton
class ThreadSyncExecutor(SyncExecutor):
    """同步执行器，异步任务运行于线程池内，单例"""

    __slots__ = ("_pool",)

    def __init__(self, max_workers: int | None = None):
        """
        初始化线程池
        Args:
            max_workers: 线程数，默认为min(32, (os.cpu_count() or 1) + 4)
        """
        self._pool = ThreadPoolExecutor(max_workers)

    def run(
        self,
        func: Callable[_P, Coroutine[_YT, _ST, _T]],
        *args: _P.args,
        **kwargs: _P.kwargs
    ) -> _T:
        """
        运行异步函数并同步返回结果，阻塞直至返回结果
        Args:
            func: 异步函数
            *args: func的位置参数
            **kwargs: func的关键字参数

        Returns:
            func的返回值
        """
        fut: Future[_T] = self._pool.submit(self._async_run, *(func, *args), **kwargs)
        return fut.result()


def run_thread_sync(
    func: Callable[_P, Coroutine[_YT, _ST, _T]], *args: _P.args, **kwargs: _P.kwargs
) -> _T:
    """
    使用线程池运行异步函数并同步返回结果，阻塞直至返回结果
    Args:
        func: 异步函数
        *args: func的位置参数
        **kwargs: func的关键字参数

    Returns:
        func的返回值
    """
    return ThreadSyncExecutor().run(func, *args, **kwargs)


def thread_sync(func: Callable[_P, Coroutine[_YT, _ST, _T]]) -> Callable[_P, _T]:
    """
    被装饰的异步函数将在新线程中运行，阻塞直至返回结果，可被视为同步函数
    Args:
        func: 异步函数

    Returns:
        同步化的func
    """

    @functools.wraps(func)
    def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _T:
        return run_thread_sync(func, *args, **kwargs)

    return wrapper


def run_process_sync(
    func: Callable[_P, Coroutine[_YT, _ST, _T]], *args: _P.args, **kwargs: _P.kwargs
) -> _T:
    """
    使用进程池运行异步函数并同步返回结果，阻塞直至返回结果
    Args:
        func: 异步函数
        *args: func的位置参数
        **kwargs: func的关键字参数

    Returns:
        func的返回值
    """
    return ProcessSyncExecutor().run(func, *args, **kwargs)


def process_sync(func: Callable[_P, Coroutine[_YT, _ST, _T]]) -> Callable[_P, _T]:
    """
    被装饰的异步函数将在新进程中运行，阻塞直至返回结果，可被视为同步函数
    Args:
        func: 异步函数

    Returns:
        同步化的func
    """

    @functools.wraps(func)
    def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _T:
        return run_process_sync(func, *args, **kwargs)

    return wrapper


sync = thread_sync  # thread_sync的开销比process_sync更小，故将其作为默认同步化装饰器
