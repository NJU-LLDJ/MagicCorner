from collections.abc import Callable


class MySQLDataType:
    """MySQL数据类型基类，用户不应该直接使用该类，而是使用该类的实例"""

    __slots__ = (
        "_name",
        "_auto_increment",
        "_not_null",
        "_primary_key",
        "_required",
        "_str",
        "_validation",
    )

    def __init__(
        self,
        name: str,
        required: int = 0,
        validation: Callable[[...], bool] | None = None,
    ):
        """
        初始化类型
        Args:
            name: 类型名
            required: 需要的参数个数
            validation: 验证函数
        """
        self._name = name
        self._auto_increment = False
        self._not_null = False
        self._primary_key = False
        self._required = required
        self._str = name  # 防止用户直接使用该类，例如：INT，而不是INT()
        self._validation = validation

    @property
    def name(self) -> str:
        return self._name

    @property
    def auto_increment(self) -> bool:
        return self._auto_increment

    @property
    def not_null(self) -> bool:
        return self._not_null

    @property
    def primary_key(self) -> bool:
        return self._primary_key

    def __call__(
        self,
        *args,
        auto_increment: bool = False,
        not_null: bool = False,
        primary_key: bool = False,
    ):
        type_str = self._name
        if self._required:
            if not self._validation(*args):
                raise ValueError("参数不合法")
            type_str = f"{self._name}({','.join(map(str, args))})"
        elif len(args):
            raise ValueError("该类型不需要参数")
        if auto_increment:
            type_str += " AUTO_INCREMENT"
        if not_null:
            type_str += " NOT NULL"
        if primary_key:
            type_str += " PRIMARY KEY"
        inst = MySQLDataType(self._name, self._required, self._validation)
        inst._auto_increment = auto_increment
        inst._not_null = not_null
        inst._primary_key = primary_key
        inst._str = type_str
        return inst

    def __str__(self):
        return self._str


# 数值类型
TINYINT = MySQLDataType("TINYINT")
SMALLINT = MySQLDataType("SMALLINT")
MEDIUMINT = MySQLDataType("MEDIUMINT")
INT = MySQLDataType("INT")
BIGINT = MySQLDataType("BIGINT")
FLOAT = MySQLDataType("FLOAT")
DOUBLE = MySQLDataType("DOUBLE")
DECIMAL = MySQLDataType(
    "DECIMAL", 2, lambda p, d: p >= d and 0 < p <= 65 and 0 <= d < 31
)

# 日期类型
DATE = MySQLDataType("DATE")
DATETIME = MySQLDataType("DATETIME")
TIMESTAMP = MySQLDataType("TIMESTAMP")
TIME = MySQLDataType("TIME")
YEAR = MySQLDataType("YEAR")

# 字符串类型
CHAR = MySQLDataType("CHAR", 1, lambda l: 0 < l <= 255)
VARCHAR = MySQLDataType("VARCHAR", 1, lambda l: 0 < l <= 65535)
BINARY = MySQLDataType("BINARY", 1, lambda l: 0 < l <= 255)
VARBINARY = MySQLDataType("VARBINARY", 1, lambda l: 0 < l <= 65535)
TINYBLOB = MySQLDataType("TINYBLOB")
BLOB = MySQLDataType("BLOB")
MEDIUMBLOB = MySQLDataType("MEDIUMBLOB")
LONGBLOB = MySQLDataType("LONGBLOB")
TINYTEXT = MySQLDataType("TINYTEXT")
TEXT = MySQLDataType("TEXT")
MEDIUMTEXT = MySQLDataType("MEDIUMTEXT")
LONGTEXT = MySQLDataType("LONGTEXT")


_types: dict[str, MySQLDataType] = {}

for k, v in globals().copy().items():
    if isinstance(v, MySQLDataType):
        _types[k] = v


def get(name: str) -> MySQLDataType | None:
    """
    获取MySQL数据类型
    Args:
        name: 类型名

    Returns:
        MySQL数据类型，不存在则返回None
    """
    return _types.get(name, None)
