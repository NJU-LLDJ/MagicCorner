import time
from sys import stderr
from typing import Callable


def type_name(obj: object) -> str:
    return type(obj).__qualname__


def debug(file=stderr, flush: bool = True):
    def mid(func: Callable):
        def inner(*args, **kwargs):
            print(
                f"{type(func).__name__} {func.__qualname__}:\n"
                + "args:\n{}\n".format(
                    f"\n".join(
                        f"{i} [{type_name(arg)}]: {arg}" for i, arg in enumerate(args)
                    )
                )
                + "kwargs:\n{}".format(
                    "\n".join(
                        f"[{type_name(k)}] {k}: [{type_name(v)}] {v}"
                        for k, v in kwargs.items()
                    )
                ),
                file=file,
                flush=flush,
            )
            start = time.process_time_ns()
            result = func(*args, **kwargs)
            end = time.process_time_ns()

            print(
                f"result [{type_name(result)}]: {result}\n"
                f"time cost: {end - start} ns",
                file=file,
                flush=flush,
            )
            print("-" * 50, file=file, flush=flush)
            return result

        return inner

    return mid


def logging(level: str = "INFO"):
    def mid(func: Callable):
        def inner(*args, **kwargs):
            print(f"[{level}]: enter {type(func).__name__} {func.__qualname__}")
            return func(*args, **kwargs)

        return inner

    return mid
