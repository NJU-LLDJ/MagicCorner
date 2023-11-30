from functools import partial

from db.types import MySQLDataType
from db._base import BaseDB, BaseDBConfig, _sync_opr, _async_opr
from db.table import Table


class DataBase(BaseDB[Table]):
    """数据库"""

    def __setitem__(self, __key, __value):
        self.create(__key)

    def __delitem__(self, __key):
        self.drop(__key)

    def __getitem__(self, __key):
        return self._data.get(__key, None)

    def __len__(self):
        self._update_table()
        return len(self._data)

    def __iter__(self):
        self._update_table()
        return iter(self._data)

    def __init__(self, name: str, config: BaseDBConfig):
        super().__init__(config, name, None, None, True)
        self._config = config
        self.connect = partial(super().connect, db=name)
        self.connect_async = partial(super().connect_async, db=name)

    @_sync_opr
    def _update_table(self):
        for name in self.execute("SHOW TABLES;"):
            self._data.setdefault(name[0])

    @_async_opr
    async def _update_table_async(self):
        for name in await self.execute_async("SHOW TABLES;"):
            self._data.setdefault(name[0])

    def _create_value(self, name: str) -> Table:
        table = Table(self._config, name, self._sync_conn, self._async_pool)
        self._data[name] = table
        return table

    @staticmethod
    def _create_sql(name: str, **field: MySQLDataType) -> str:
        fields = f"{','.join([f'{f} {t}' for f, t in field.items()])}"
        return f"CREATE TABLE IF NOT EXISTS {name} ({fields});"

    @_sync_opr
    def create(self, name: str, **field: MySQLDataType) -> Table:
        """
        创建表
        Args:
            name: 表名
            **field: 字段名和类型

        Returns:
            表对象
        """
        self.execute(self._create_sql(name, **field))
        self._update_table()
        return self._create_value(name)

    @_async_opr
    async def create_async(self, name: str, **field: MySQLDataType) -> Table:
        """
        异步创建表
        Args:
            name: 表名
            **field: 字段名和类型

        Returns:
            表对象
        """
        await self.execute_async(self._create_sql(name, **field))
        await self._update_table_async()
        return self._create_value(name)

    @_sync_opr
    def drop(self, name: str):
        """
        删除表
        Args:
            name: 表名
        """
        self.execute(f"DROP TABLE {name};")
        self._update_table()
        if name in self._data:
            del self._data[name]

    @_async_opr
    async def drop_async(self, name: str):
        """
        异步删除表
        Args:
            name: 表名
        """
        await self.execute_async(f"DROP TABLE {name};")
        await self._update_table_async()
        if name in self._data:
            del self._data[name]

    @_sync_opr
    def exists(self, name: str) -> bool:
        """判断表是否存在"""
        self._update_table()
        return name in self._data

    @_async_opr
    async def exists_async(self, name: str) -> bool:
        """异步判断表是否存在"""
        await self._update_table_async()
        return name in self._data
