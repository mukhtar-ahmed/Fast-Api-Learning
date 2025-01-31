from fastapi import FastAPI, Body
from pydantic import BaseModel, Field
app = FastAPI()

class Book:
    id:int
    title:str
    author: str
    description: str
    rating: int
    
    def __init__(self,id,title,author,description,rating):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating

class BookIn(BaseModel):
    id:int
    title:str = Field(min_length=3)
    author: str = Field(min_length=3)
    description: str = Field(min_length=10)
    rating: int = Field(gt=0, lt=6)

BOOKS = [
    Book(1,'Dev ops' , 'Mukhtar Ahmed','Its nice book',5),
    Book(2,'Python' , 'Mukhtar Ahmed','Its nice book',4),
    Book(3,'Java' , 'Mukhtar Ahmed','Its nice book',3),
    Book(3,'c++' , 'Awais','Average',2),
]

@app.get('/books')
def read_books():
    return {
        'message': 'Sucess',
        'total': len(BOOKS),
        'data': BOOKS
    }
    
@app.post("/books/create-book")
def create_book(book : BookIn):
    BOOKS.append(find_book_id(Book(**book.model_dump())))
    return {
        'message': 'Sucess',
        'total': len(BOOKS),
        'data': BOOKS
    }
    
def find_book_id(book: Book):
    if(len(BOOKS) > 0):
        book.id = BOOKS[-1].id + 1
    else:
        book.id = 1
        
    return book