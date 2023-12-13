from typing import Generic, TypeVar, Optional, TypeVarTuple

_T = TypeVar("_T")
_Ts = TypeVarTuple("_Ts")


class DTypeOption(Generic[_T]):
    """
    MySQL数据类型选项，用于描述MySQL数据类型，以大写形式输出

    例如：
    >>> o = DTypeOption(auto_increment=True, default=0, not_null=True, primary_key=True)
    >>> assert str(o) == "AUTO_INCREMENT DEFAULT 0 NOT NULL PRIMARY KEY"
    """

    __slots__ = ("auto_increment", "default", "not_null", "primary_key", "extras")

    def __init__(
        self,
        auto_increment: bool = False,
        default: Optional[_T] = None,
        not_null: bool = False,
        primary_key: bool = False,
        *extras: str,
    ):
        """
        初始化MySQL数据类型选项
        Args:
            auto_increment: 是否自增，默认为False
            default: 默认值，默认为None
            not_null: 是否非空，默认为False
            primary_key: 是否主键，默认为False
            *extras: 其他未提到的选项，如UNSIGNED、ZEROFILL等
        """
        self.auto_increment = auto_increment
        self.default = default
        self.not_null = not_null
        self.primary_key = primary_key
        self.extras = tuple(e.upper() for e in extras)

    def __str__(self) -> str:
        s = []
        if self.auto_increment:
            s.append("AUTO_INCREMENT")
        if self.default is not None:
            s.append(f"DEFAULT {self.default}")
        if self.not_null:
            s.append("NOT NULL")
        if self.primary_key:
            s.append("PRIMARY KEY")
        s.extend(self.extras)
        return " ".join(s)


class DType(Generic[_T, *_Ts]):
    """
    MySQL数据类型基类，请勿直接使用该类，而是使用DTypes类中的数据类型

    泛型参数中，第一个参数(_T)为数据类型，后面的参数(*_Ts)为数据类型参数。

    举例来说，Decimal继承了DType[float, int, int]，
    其中float为数据类型，意思是Decimal保存了一个浮点数，
    int, int为数据类型参数，意思是Decimal的参数为两个整数，分别表示精度和小数位数。
    """

    __slots__ = ("_args", "_option", "_field", "_value")

    @classmethod
    def dtype(cls):
        """数据类型名"""
        return cls.__name__.upper()

    def __init__(self, *args: *_Ts, option: Optional[DTypeOption] = None):
        """
        初始化MySQL数据类型对象
        Args:
            *args: 数据类型参数，如DECIMAL(10, 2)中的10和2
            option: 数据类型选项，默认为None
        """
        if self.__class__ is DType:
            raise TypeError(
                "DType shouldn't be instantiated directly."
                " Use attributes of DTypes instead."
            )
        self._args = args
        self._validate()
        self._option = option
        self._field: str
        self._value: Optional[_T] = None

    def __str__(self):
        if self._args:
            args = f"({','.join(map(str, self._args))})"
        else:
            args = ""
        if self._option:
            option = str(self._option)
        else:
            option = ""
        return f"{self.dtype()}{args} {option}".strip()

    def __set_name__(self, owner: object, name: str):
        self._field = name

    def __get__(self, instance: object, owner: type) -> "DType[_T, *_Ts]":
        return self

    def __set__(self, instance: object, value: Optional[_T]):
        self._value = value

    def _validate(self) -> None:
        """验证数据类型参数是否合法"""
        # 1. 获取参数类型元组，如DType[int, str, float]的参数类型元组为(str, float)
        # noinspection PyUnresolvedReferences
        expect: tuple[type] = self.__class__.__orig_bases__[0].__args__[1:]
        # 2. 验证参数个数是否正确
        if len(self._args) != len(expect):
            raise ValueError(
                f"{self.dtype()} expects {len(expect)} positional arguments,"
                f" got {len(self._args)}"
            )
        # 3. 验证参数类型是否正确
        for i, (arg, arg_type) in enumerate(zip(self._args, expect)):
            if not isinstance(arg, arg_type):
                raise ValueError(
                    f"Argument {i} of {self.dtype()} should be "
                    f"an instance of {arg_type}, got {arg}, type {type(arg)}"
                )


class DTypes:
    """MySQL数据类型"""

    __slots__ = ()

    # 数值类型
    class TinyInt(DType[int]):
        pass

    class SmallInt(DType[int]):
        pass

    class MediumInt(DType[int]):
        pass

    class Int(DType[int]):
        pass

    class BigInt(DType[int]):
        pass

    class Float(DType[float]):
        pass

    class Double(DType[float]):
        pass

    class Decimal(DType[float, int, int]):
        def _validate(self) -> None:
            super()._validate()
            p, s = self._args
            if p <= 0 or p > 65:
                raise ValueError(f"Expected precision in [1, 65], got {p}")
            if s < 0 or s > 30:
                raise ValueError(f"Expected scale in [0, 30], got {s}")
            if p < s:
                raise ValueError(f"Expected precision >= scale, got {p} < {s}")

    # 日期和时间类型
    class Date(DType[str]):
        pass

    class Time(DType[str]):
        pass

    class DateTime(DType[str]):
        pass

    class TimeStamp(DType[str]):
        pass

    class Year(DType[str]):
        pass

    # 文本类型
    class Char(DType[str, int]):
        def _validate(self) -> None:
            super()._validate()
            length = self._args[0]
            if length <= 0 or length > 255:
                raise ValueError(f"Expected length in [1, 255], got {length}")

    class VarChar(DType[str, int]):
        def _validate(self) -> None:
            super()._validate()
            length = self._args[0]
            if length <= 0 or length > 65535:
                raise ValueError(f"Expected length in [1, 65535], got {length}")

    class TinyText(DType[str]):
        pass

    class Text(DType[str]):
        pass

    class MediumText(DType[str]):
        pass

    class LongText(DType[str]):
        pass

    # 二进制类型
    class Binary(DType[bytes, int]):
        def _validate(self) -> None:
            super()._validate()
            length = self._args[0]
            if length <= 0 or length > 255:
                raise ValueError(f"Expected length in [1, 255], got {length}")

    class VarBinary(DType[bytes, int]):
        def _validate(self) -> None:
            super()._validate()
            length = self._args[0]
            if length <= 0 or length > 65535:
                raise ValueError(f"Expected length in [1, 65535], got {length}")

    class TinyBlob(DType[bytes]):
        pass

    class Blob(DType[bytes]):
        pass

    class MediumBlob(DType[bytes]):
        pass

    class LongBlob(DType[bytes]):
        pass


class TestTable:
    id = DTypes.Int(option=DTypeOption(auto_increment=True, primary_key=True))
    name = DTypes.VarChar(12345)
    age = DTypes.Int()


t = TestTable()
t.id = 3
