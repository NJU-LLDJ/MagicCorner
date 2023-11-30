from fastapi import APIRouter

from model.v1.book import Book

book = APIRouter()


@book.get("/{bid}/")
async def get_book(bid: int) -> Book:
    return await Book.get_by_id(bid)
