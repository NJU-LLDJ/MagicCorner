from abc import ABC, abstractmethod

from pydantic import BaseModel

from db import Table, MySQLDataType


class CRUD(BaseModel, ABC):
    """CRUD基类"""

    _table: Table

    @classmethod
    @abstractmethod
    def table_name(cls) -> str:
        """表名"""

    @classmethod
    @abstractmethod
    def table_columns(cls) -> dict[str, MySQLDataType]:
        """列名和类型"""

    async def insert(self):
        await self._table.insert_async(**self.model_dump())
