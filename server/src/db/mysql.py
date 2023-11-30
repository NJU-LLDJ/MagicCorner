from db._base import BaseDB, BaseDBConfig, _sync_opr, _async_opr
from db.database import DataBase


class MySQL(BaseDB[DataBase]):
    """
    MySQL数据库

    同步用法：
    mysql = MySQL(config)
    mysql.create("database_name")
    mysql.use("database_name")
    mysql.drop("database_name")

    异步用法：
    mysql = MySQL(config)
    await mysql.create_async("database_name")
    await mysql.use_async("database_name")
    await mysql.drop_async("database_name")

    字典用法：
    mysql = MySQL(config)
    mysql["database_name"] = None # 创建数据库，None可以是任何值
    database = mysql["database_name"] # 获取数据库对象
    del mysql["database_name"] # 删除数据库
    """

    def __setitem__(self, __key, __value):
        # 这个方法看起来很怪，没有使用__value的值
        # 但是这个方法是为了实现类似字典的用法
        # 例如：mysql["database_name"] = None
        # 这样就可以在字典中创建一个数据库对象
        # 然后再通过database = mysql["database_name"]获取数据库对象
        # 实际不推荐这样用，不如直接mysql.create("database_name")
        self.create(__key)

    def __delitem__(self, __key):
        self.drop(__key)

    def __getitem__(self, __key):
        self.use(__key)

    def __len__(self):
        return len(self.database_names)

    def __iter__(self):
        return iter(self.database_names)

    def __init__(
        self,
        config: BaseDBConfig | None = None,
        host: str | None = None,
        port: int | None = None,
        user: str | None = None,
        password: str | None = None,
    ):
        """
        初始化MySQL数据库对象

        如果config不为None，则使用config初始化，否则使用host、port、user、password初始化。

        Args:
            config: 配置对象
            host: IP地址
            port: 端口
            user: 用户名
            password: 密码
        """
        if config is None:
            config = BaseDBConfig(
                host=host,
                port=port,
                user=user,
                password=password,
            )
        super().__init__(config, "MySQL", None, None, True)

    @property
    def database_names(self) -> tuple[str]:
        """获得数据库名列表，等同于Show Databases;"""
        self._update_database()
        return tuple(self._data.keys())

    @_sync_opr
    def _update_database(self):
        for name in self.execute("SHOW DATABASES;"):
            self._data.setdefault(name[0])

    @_async_opr
    async def _update_database_async(self):
        for name in await self.execute_async("SHOW DATABASES;"):
            self._data.setdefault(name[0])

    def _create_value(self, name: str) -> DataBase:
        database = DataBase(name, self._config)
        self._data[name] = database
        return database

    @_sync_opr
    def use(self, name: str) -> DataBase:
        """
        选择数据库
        Args:
            name: 数据库名

        Returns:
            数据库对象
        """
        # 如果在数据库字典中存在该数据库
        if name in self._data:
            if self._data[name] is None:
                self._create_value(name)
            return self._data[name]
        # 如果不存在该数据库，更新数据库字典
        self._update_database()
        if name not in self._data:
            raise UserWarning(f"Database {name} is unavailable or not exists.")
        # 初始化该数据库
        return self._create_value(name)

    @_async_opr
    async def use_async(self, name: str) -> DataBase:
        """
        异步选择数据库
        Args:
            name: 数据库名

        Returns:
            数据库对象
        """
        # 如果在数据库字典中存在该数据库
        if name in self._data:
            if self._data[name] is None:
                self._create_value(name)
            return self._data[name]
        # 如果不存在该数据库，更新数据库字典
        await self._update_database_async()
        if name not in self._data:
            raise UserWarning(f"Database {name} is unavailable or not exists.")
        # 初始化该数据库
        return self._create_value(name)

    @_sync_opr
    def create(self, name: str) -> DataBase:
        """
        创建数据库
        Args:
            name: 数据库名

        Returns:
            数据库对象
        """
        self.execute(f"CREATE DATABASE IF NOT EXISTS {name};")
        self._update_database()
        return self._create_value(name)

    @_async_opr
    async def create_async(self, name: str) -> DataBase:
        """
        异步创建数据库
        Args:
            name: 数据库名

        Returns:
            数据库对象
        """
        await self.execute_async(f"CREATE DATABASE IF NOT EXISTS {name};")
        await self._update_database_async()
        return self._create_value(name)

    @_sync_opr
    def drop(self, name: str):
        """
        删除数据库
        Args:
            name: 数据库名
        """
        self.execute(f"DROP DATABASE {name};")
        self._update_database()
        if name in self._data:
            del self._data[name]

    @_async_opr
    async def drop_async(self, name: str):
        """
        异步删除数据库
        Args:
            name: 数据库名
        """
        await self.execute_async(f"DROP DATABASE {name};")
        await self._update_database_async()
        if name in self._data:
            del self._data[name]

    @_sync_opr
    def exists(self, name: str) -> bool:
        """
        判断数据库是否存在
        Args:
            name: 数据库名

        Returns:
            是否存在
        """
        self._update_database()
        return name in self._data

    @_async_opr
    async def exists_async(self, name: str) -> bool:
        """
        异步判断数据库是否存在
        Args:
            name: 数据库名

        Returns:
            是否存在
        """
        await self._update_database_async()
        return name in self._data
