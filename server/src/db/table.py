from db._base import BaseDB, _DB, _async_opr, _sync_opr, BaseDBConfig
from db.types import MySQLDataType


class Table(BaseDB[tuple[tuple]]):
    """数据表"""

    def _create_value(self, *args, **kwargs) -> _DB:
        raise NotImplementedError

    def __setitem__(self, __key, __value):
        self.update(__key, **__value)

    def __delitem__(self, __key):
        self.delete(__key)

    def __getitem__(self, __key):
        return self.select(__key)

    def __len__(self):
        return self.nrow

    def __iter__(self):
        return iter(self.select())

    def __init__(
        self,
        config: BaseDBConfig,
        name: str,
        sync_conn=None,
        async_pool=None,
    ):
        super().__init__(config, name, sync_conn, async_pool, False)

    @property
    @_sync_opr
    def nrow(self) -> int:
        """获取表中的行数"""
        return self.execute(f"SELECT COUNT(*) FROM {self._name};")[0][0]

    @_async_opr
    async def nrow_async(self) -> int:
        """异步获取表中的行数"""
        sql = f"SELECT COUNT(*) FROM {self._name};"
        return (await self.execute_async(sql))[0][0]  # execute返回((4,),)

    @property
    @_sync_opr
    def ncol(self) -> int:
        """获取表中的列数"""
        return len(self.execute(f"SHOW COLUMNS FROM {self._name};"))

    @_async_opr
    async def ncol_async(self) -> int:
        """异步获取表中的列数"""
        sql = f"SHOW COLUMNS FROM {self._name};"
        return len(await self.execute_async(sql))

    @property
    @_sync_opr
    def size(self) -> tuple[int, int]:
        """获取表的大小, row, col"""
        return self.nrow, self.ncol

    @_async_opr
    async def size_async(self) -> tuple[int, int]:
        """异步获取表的大小, row, col"""
        return await self.nrow_async(), await self.ncol_async()

    @_sync_opr
    def drop(self):
        """删除表"""
        self.execute(f"DROP TABLE {self._name};")

    @_async_opr
    async def drop_async(self):
        """异步删除表"""
        await self.execute_async(f"DROP TABLE {self._name};")

    @_sync_opr
    def truncate(self):
        """清空表"""
        self.execute(f"TRUNCATE TABLE {self._name};")

    @_async_opr
    async def truncate_async(self):
        """异步清空表"""
        await self.execute_async(f"TRUNCATE TABLE {self._name};")

    def _select_sql(
        self,
        *column: str,
        distinct: bool = False,
        where: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> str:
        columns = ",".join(column) or "*"
        sql = f"SELECT {'DISTINCT ' if distinct else ''}{columns} FROM {self._name}"
        if where is not None:
            sql += f" WHERE {where}"
        if limit is not None:
            sql += f" LIMIT {limit}"
        if offset is not None:
            sql += f" OFFSET {offset}"
        sql += ";"
        return sql

    @_sync_opr
    def select(
        self,
        *column: str,
        distinct: bool = False,
        where: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> tuple[tuple]:
        sql = self._select_sql(
            *column, distinct=distinct, where=where, limit=limit, offset=offset
        )
        return self.execute(sql)

    @_async_opr
    async def select_async(
        self,
        *column: str,
        distinct: bool = False,
        where: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> tuple[tuple]:
        sql = self._select_sql(
            *column, distinct=distinct, where=where, limit=limit, offset=offset
        )
        return await self.execute_async(sql)

    def _insert_sql(self, **column) -> str:
        columns = ",".join(column.keys())
        values = ",".join(map(str, column.values()))
        return f"INSERT INTO {self._name} ({columns}) VALUES ({values});"

    @_sync_opr
    def insert(self, **column):
        """
        插入数据
        Args:
            **column: 列名和值
        """
        # print(self._insert_sql(**column))
        self.execute(self._insert_sql(**column))

    @_async_opr
    async def insert_async(self, **column):
        """
        异步插入数据
        Args:
            **column: 列名和值
        """
        await self.execute_async(self._insert_sql(**column))

    @_sync_opr
    def insert_many(self, *columns: dict[str, ...]):
        """
        插入多条数据
        Args:
            *columns: 列名和值的字典
        """
        for column in columns:
            self.insert(**column)

    @_async_opr
    async def insert_many_async(self, *columns: dict[str, ...]):
        """
        异步插入多条数据
        Args:
            *columns: 列名和值的字典
        """
        for column in columns:
            await self.insert_async(**column)

    def _update_sql(self, where: str | None, **columns):
        # noinspection SqlWithoutWhere
        sql = f"UPDATE {self._name} SET {','.join([f'{k}={v}' for k, v in columns.items()])}"
        if where is not None:
            sql += f" WHERE {where}"
        sql += ";"
        return sql

    @_sync_opr
    def update(self, where: str | None, **column):
        """
        更新数据
        Args:
            where: 条件, 如果为None, 则更新所有数据
            **column: 列名和值
        """
        self.execute(self._update_sql(where, **column))

    @_async_opr
    async def update_async(self, where: str | None, **column):
        """
        异步更新数据
        Args:
            where: 条件, 如果为None, 则更新所有数据
            **column: 列名和值
        """
        await self.execute_async(self._update_sql(where, **column))

    def _delete_sql(self, where: str | None) -> str:
        # noinspection SqlWithoutWhere
        sql = f"DELETE FROM {self._name}"
        if where is not None:
            sql += f" WHERE {where}"
        sql += ";"
        return sql

    @_sync_opr
    def delete(self, where: str | None):
        """
        删除数据
        Args:
            where: 条件, 如果为None, 则删除所有数据
        """
        self.execute(self._delete_sql(where))

    @_async_opr
    async def delete_async(self, where: str | None):
        """
        异步删除数据
        Args:
            where: 条件, 如果为None, 则删除所有数据
        """
        await self.execute_async(self._delete_sql(where))

    @_sync_opr
    def add_columns(self, **column: MySQLDataType):
        """
        在所有列末尾添加列
        Args:
            **column: 列名和类型
        """
        self.execute(
            f"ALTER TABLE {self._name} "
            f"ADD {','.join([f'{f} {t}' for f, t in column.items()])};"
        )

    @_async_opr
    async def add_columns_async(self, **column: MySQLDataType):
        """
        异步在所有列末尾添加列
        Args:
            **column: 列名和类型
        """
        await self.execute_async(
            f"ALTER TABLE {self._name} "
            f"ADD {','.join([f'{f} {t}' for f, t in column.items()])};"
        )

    @_sync_opr
    def modify_columns(self, **column: MySQLDataType):
        """
        修改列的类型
        Args:
            **column: 列名和类型
        """
        self.execute(
            f"ALTER TABLE {self._name} "
            f"MODIFY {','.join([f'{f} {t}' for f, t in column.items()])};"
        )

    @_async_opr
    async def modify_columns_async(self, **column: MySQLDataType):
        """
        异步修改列的类型
        Args:
            **column: 列名和类型
        """
        await self.execute_async(
            f"ALTER TABLE {self._name} "
            f"MODIFY {','.join([f'{f} {t}' for f, t in column.items()])};"
        )

    @_sync_opr
    def drop_columns(self, *column: str):
        """
        删除列
        Args:
            *column: 列名
        """
        self.execute(f"ALTER TABLE {self._name} DROP {','.join(column)};")

    @_async_opr
    async def drop_columns_async(self, *column: str):
        """
        异步删除列
        Args:
            *column: 列名
        """
        await self.execute_async(f"ALTER TABLE {self._name} DROP {','.join(column)};")
