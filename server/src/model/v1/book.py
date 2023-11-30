from pydantic import model_validator

from db.types import *
from model.v1.crud import CRUD


class Book(CRUD):
    rating: float
    pic: str
    intro: str
    author_intro: str
    card_subtitle: str
    id: int
    buylinks_url: str
    author: str
    price: str
    translator: str
    catalog: str
    press: str
    pages: str
    title: str
    tag: str

    @classmethod
    def table_name(cls) -> str:
        return cls.__name__

    @classmethod
    def table_columns(cls) -> dict[str, MySQLDataType]:
        return {
            "rating": FLOAT(),
            "pic": VARCHAR(255),
            "intro": TEXT(),
            "author_intro": TEXT(),
            "card_subtitle": TEXT(),
            "id": INT(primary_key=True),
            "buylinks_url": VARCHAR(255),
            "author": TINYTEXT(),
            "price": TINYTEXT(),
            "translator": TINYTEXT(),
            "catalog": TEXT(),
            "press": TINYTEXT(),
            "pages": TINYTEXT(),
            "title": TINYTEXT(),
            "tag": TINYTEXT(),
        }

    # noinspection PyNestedDecorators
    @model_validator(mode="before")
    @classmethod
    def __convert_rating_and_pic(cls, data):
        """
        豆瓣API返回的json：
        ```
        {
            "rating": {
                "value": 9.2
            },
            "pic": {
                "normal": "https://..."
            },
        }
        ```
        而前端要求的是：
        ```
        {
            "rating": 9.2,
            "pic": "https://...",
        }
        ```
        此函数执行数据预处理操作，将字典修改为前端需要的格式
        """

        def convert_field_to_sub_field(field: str, sub_field: str, default):
            if field in data and isinstance(data[field], dict):
                data[field] = data[field].get(sub_field, default)
            else:
                data[field] = default

        if isinstance(data, dict):
            convert_field_to_sub_field("rating", "value", 0.0)
            convert_field_to_sub_field("pic", "normal", "")
            data["author"] = ",".join(data.get("author", []))
            data["price"] = ",".join(data.get("price", []))
            data["translator"] = ",".join(data.get("translator", []))
            data["press"] = ",".join(data.get("press", []))
            data["pages"] = ",".join(data.get("pages", []))
            if "tag" not in data:
                data["tag"] = ""
        return data

    @model_validator(mode="after")
    def add_single_quote_to_str(self):
        """
        将字符串类型的字段添加单引号
        """
        from pymysql.converters import escape_string

        for f in self.model_fields.keys():
            if f not in ("id", "rating"):
                setattr(
                    self, f, f"'{getattr(self, escape_string(f)).replace('%', '%%')}'"
                )
