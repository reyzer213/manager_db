from fastapi import FastAPI, HTTPException
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from pydantic import BaseModel, Field
from typing import Dict, List
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from passlib.hash import bcrypt

app = FastAPI()
templates = Jinja2Templates(directory="templates")

SQLALCHEMY_DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)


Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String, unique=True, index=True)
    password = Column(String)

Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

hashed_password = bcrypt.hash("Бульбулятор2009")
user = User(login="Антоха2009", password=hashed_password)
db.add(user)
db.commit()
db.close()

class Book(BaseModel):
    Title: str = Field(min_length=1, description="БЛА-БЛА")
    Author: str = Field(min_length=3, max_length=30, description="БЛА-БЛА")
    Pages: int = Field(gt=10, description="БЛА-БЛА")


library: Dict[str, List[Book]] = {}


@app.post("/books/")
def create_Book(book: Book):
    if book.Author not in library:
        library[book.Author] = []
    library[book.Author].append(book)
    return {"message": "Книжка додана і т.д"}


@app.get("/books/{author}")
def get_books_by_author(author: str):
    if author not in library:
        raise HTTPException(status_code=404, detail="Автора не знайдено")
    return library[author]


@app.put("/books/{author}/{title}")
def update_book(author: str, title: str, new_pages: int):
    if author not in library or not any(book.Title == title for book in library[author]):
        raise HTTPException(status_code=404, detail="Книжку не знайдено")
    for book in library[author]:
        if book.Title == title:
            book.Pages = new_pages  # Changed attribute name
            return {"message": "Книжка оновлена успішно"}


@app.delete("/books/{author}/{title}")
def delete_book(author: str, title: str):
    if author not in library or not any(book.Title == title for book in library[author]):
        raise HTTPException(status_code=404, detail="Книжку не знайдено")
    library[author] = [book for book in library[author] if book.Title != title]
    return {"message": "Книжка видалена успішно"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
