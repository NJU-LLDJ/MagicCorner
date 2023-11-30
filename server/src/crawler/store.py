import asyncio
import csv
import threading

import aiohttp

from db import MySQL, BaseDBConfig, DataBase, Table
from model.v1 import Book


def split_dict(dictionary, n):
    # 计算每份的大小
    avg_items = len(dictionary) // n
    remainder = len(dictionary) % n
    result = []
    current_start = 0
    for i in range(n):
        # 计算当前份的大小
        current_size = avg_items + (1 if i < remainder else 0)
        # 获取当前份的字典切片
        current_dict = {
            key: dictionary[key]
            for key in list(dictionary.keys())[
                current_start : current_start + current_size
            ]
        }
        # 将当前份添加到结果列表
        result.append(current_dict)
        # 更新下一份的起始位置
        current_start += current_size
    return result


async def main():
    with open("server/data/data.csv", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        books: dict[int, str] = {}
        for row in reader:
            bid = int(row[0])
            if bid in books:
                books[bid] += f",{row[1]}"
            else:
                books[bid] = row[1]
        books_split = split_dict(books, 20)
    processes = []
    for i in range(20):
        processes.append(
            threading.Thread(target=asyncio.run, args=(process(books_split[i]),))
        )
    for p in processes:
        p.start()

    for p in processes:
        p.join()


async def process(books: dict[int, str]):
    mysql = MySQL(BaseDBConfig.from_file("server/config/db.json"))
    mc: DataBase = await mysql.use_async("magiccorner")
    book_table: Table = await mc.create_async(Book.table_name(), **Book.table_columns())

    url = "https://frodo.douban.com/api/v2/book/{}?apiKey=0ac44ae016490db2204ce0a042db2916"
    headers = {
        "Cache-Control": "no-cache",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "User-Agent": "MicroMessenger/",
        "Referer": "https://servicewechat.com/wx2f9b06c1de1ccfca/91/page-frame.html",
    }
    async with aiohttp.ClientSession() as session:
        for bid, tag in books.items():
            try:
                async with session.get(url.format(bid), headers=headers) as response:
                    book = Book(**await response.json())
                    book.tag = f"'{tag}'"
                    await book_table.insert_async(**book.model_dump())
            except Exception as e:
                print(f"[{bid}]: {e}")

    await mc.close_async()
    await mysql.close_async()


if __name__ == "__main__":
    asyncio.run(main())
