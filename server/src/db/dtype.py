from typing import Generic, Optional, TypeAlias, TypeGuard, TypeVar, TypeVarTuple

_V = TypeVar("_V")
_Args = TypeVarTuple("_Args")


class DTypeOption(Generic[_V]):
    """
    MySQL数据类型选项，用于描述MySQL数据类型，以大写形式输出

    例如：
    >>> o = DTypeOption(auto_increment=True, default=0, not_null=True, primary_key=True)
    >>> assert str(o) == "AUTO_INCREMENT DEFAULT 0 NOT NULL PRIMARY KEY"
    """

    __slots__ = ("auto_increment", "default", "not_null", "primary_key", "extras")

    def __init__(
        self,
        *extras: str,
        auto_increment: bool = False,
        default: Optional[_V] = None,
        not_null: bool = False,
        primary_key: bool = False,
    ):
        """
        初始化MySQL数据类型选项
        Args:
            *extras: 关键字参数中未提到的选项，如UNSIGNED、ZEROFILL等
        Keyword Args:
            auto_increment: 是否自增，默认为False
            default: 默认值，默认为None
            not_null: 是否非空，默认为False
            primary_key: 是否主键，默认为False
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


class DType(Generic[_V, *_Args]):
    """
    MySQL数据类型基类，请勿直接使用该类，而是使用DTypes类中的数据类型

    泛型参数中，第一个参数(_V)为数据类型，后面的参数(*_Args)为数据类型参数。

    举例来说，Decimal继承了DType[float, int, int]，
    其中float为数据类型，意思是Decimal保存了一个浮点数，
    int, int为数据类型参数，意思是Decimal的参数为两个整数，分别表示精度和小数位数。
    """

    __slots__ = ("_args", "_option", "_field", "_value")

    @classmethod
    def dtype(cls):
        """数据类型名"""
        return cls.__name__.upper()

    @classmethod
    def real_type(cls) -> type[_V]:
        """在Python中实际使用的数据类型"""
        # noinspection PyUnresolvedReferences
        return cls.__orig_bases__[0].__args__[0]  # type: ignore

    def __init__(
        self,
        *args: *_Args,
        option: Optional[DTypeOption[_V]] = None,
    ):
        """
        初始化MySQL数据类型对象
        Args:
            args: 数据类型参数，如DECIMAL(10, 2)中的10和2
            option: 数据类型选项，默认为None
        """
        if self.__class__ is DType:
            raise TypeError(
                "DType shouldn't be instantiated directly."
                " Use attributes of DTypes instead."
            )
        self._validate_args(args)
        self._args = args
        self._option = option
        self._field: str
        self._value: Optional[_V] = None

    @property
    def args(self) -> tuple[*_Args]:
        return self._args

    @property
    def option(self) -> Optional[DTypeOption]:
        return self._option

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

    def __get__(self, instance: object, owner: type) -> Optional[_V]:
        return self._value

    def __set__(self, instance: object, value: Optional[_V]):
        self._value = value

    @classmethod
    def _validate_args(cls, args: tuple[*_Args]) -> TypeGuard[tuple[*_Args]]:
        """
        验证数据类型参数是否合法。
        具体来说，验证了参数的个数和类型是否符合泛型参数的要求。
        Args:
            args: 数据类型参数
        Raises:
            ValueError: 参数个数不正确
            TypeError: 参数类型不正确
        """
        # 1. 获取参数类型元组，如DType[int, str, float]的参数类型元组为(str, float)
        # noinspection PyUnresolvedReferences
        expect: tuple[type] = cls.__orig_bases__[0].__args__[1:]  # type: ignore
        # 2. 验证参数个数是否正确
        if len(args) != len(expect):
            raise ValueError(
                f"{cls.dtype()} expects {len(expect)} positional arguments,"
                f" got {len(args)}"
            )
        # 3. 验证参数类型是否正确
        for i, (arg, arg_type) in enumerate(zip(args, expect)):  # type: ignore
            if not isinstance(arg, arg_type):
                raise TypeError(
                    f"Argument {i} of {cls.dtype()} should be "
                    f"an instance of {arg_type}, got {arg}, type {type(arg)}"
                )
        return True

    def _validate_value(self, value: Optional[_V]) -> TypeGuard[Optional[_V]]:
        """验证数据类型值是否合法"""
        if value is None:
            if self._option is not None and self._option.not_null:
                raise ValueError(f"Field {self._field} cannot be None")
        else:
            if not isinstance(value, self.real_type()):
                raise TypeError(
                    f"Field {self._field} should be"
                    f" an instance of {self.real_type()},"
                    f" got {value}, type {type(self._value)}"
                )
        return True


# 我希望可以删除这个类，直接使用DType，但是Pycharm的语法检查一直产生恼人的Warning，
# 所以只能保留。详见 [#5](https://github.com/NJU-LLDJ/MagicCorner/issues/5)。
class NoArgsDType(DType[_V]):
    """没有参数的MySQL数据类型基类"""

    __slots__ = ()

    def __init__(self, option: Optional[DTypeOption[_V]] = None):
        """
        初始化没有参数的MySQL数据类型对象
        Args:
            option: 数据类型选项，默认为None
        """
        super().__init__(*tuple(), option=option)


Precision: TypeAlias = int
"""Decimal的第一个参数，表示精度。0 < precision <= 65，且大于等于Scale"""
Scale: TypeAlias = int
"""Decimal的第二个参数，表示小数位数。0<=scale<=30，且小于等于Precision"""
Length: TypeAlias = int
"""字符串的长度参数，表示长度。
对于Char和Binary，0 < len <= 255，
对于VarChar和VarBinary，0 < len <= 65535"""


class DTypes:
    """MySQL数据类型"""

    __slots__ = ()

    # 数值类型
    class TinyInt(NoArgsDType[int]):
        pass

    class SmallInt(NoArgsDType[int]):
        pass

    class MediumInt(NoArgsDType[int]):
        pass

    class Int(NoArgsDType[int]):
        pass

    class BigInt(NoArgsDType[int]):
        pass

    class Float(NoArgsDType[float]):
        pass

    class Double(NoArgsDType[float]):
        pass

    class Decimal(DType[float, Precision, Scale]):
        @classmethod
        def _validate_args(
            cls, args: tuple[Precision, Scale]
        ) -> TypeGuard[tuple[Precision, Scale]]:
            super()._validate_args(args)
            p, s = args
            if p <= 0 or p > 65:
                raise ValueError(f"Expected precision in [1, 65], got {p}")
            if s < 0 or s > 30:
                raise ValueError(f"Expected scale in [0, 30], got {s}")
            if p < s:
                raise ValueError(f"Expected precision >= scale, got {p} < {s}")
            return True

    # 日期和时间类型
    class Date(NoArgsDType[str]):
        pass

    class Time(NoArgsDType[str]):
        pass

    class DateTime(NoArgsDType[str]):
        pass

    class TimeStamp(NoArgsDType[str]):
        pass

    class Year(NoArgsDType[str]):
        pass

    # 文本类型
    class Char(DType[str, Length]):
        @classmethod
        def _validate_args(cls, args: tuple[Length]) -> TypeGuard[tuple[Length]]:
            super()._validate_args(args)
            length = args[0]
            if length <= 0 or length > 255:
                raise ValueError(f"Expected length in [1, 255], got {length}")
            return True

    class VarChar(DType[str, Length]):
        @classmethod
        def _validate_args(cls, args: tuple[Length]) -> TypeGuard[tuple[Length]]:
            super()._validate_args(args)
            length = args[0]
            if length <= 0 or length > 65535:
                raise ValueError(f"Expected length in [1, 65535], got {length}")
            return True

    class TinyText(NoArgsDType[str]):
        pass

    class Text(NoArgsDType[str]):
        pass

    class MediumText(NoArgsDType[str]):
        pass

    class LongText(NoArgsDType[str]):
        pass

    # 二进制类型
    class Binary(DType[bytes, Length]):
        @classmethod
        def _validate_args(cls, args: tuple[Length]) -> TypeGuard[tuple[Length]]:
            super()._validate_args(args)
            length = args[0]
            if length <= 0 or length > 255:
                raise ValueError(f"Expected length in [1, 255], got {length}")
            return True

    class VarBinary(DType[bytes, Length]):
        @classmethod
        def _validate_args(cls, args: tuple[Length]) -> TypeGuard[tuple[Length]]:
            super()._validate_args(args)
            length = args[0]
            if length <= 0 or length > 65535:
                raise ValueError(f"Expected length in [1, 65535], got {length}")
            return True

    class TinyBlob(NoArgsDType[bytes]):
        pass

    class Blob(NoArgsDType[bytes]):
        pass

    class MediumBlob(NoArgsDType[bytes]):
        pass

    class LongBlob(NoArgsDType[bytes]):
        pass
