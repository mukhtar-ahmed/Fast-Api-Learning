from fastapi import FastAPI, Path, Query, HTTPException
from pydantic import BaseModel, Field
from starlette import status

app = FastAPI()

class Book:
    id:int
    title:str
    author: str
    description: str
    rating: int
    published_date: int
    
    def __init__(self,id,title,author,description,rating,published_date):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date

class BookIn(BaseModel):
    id:int
    title:str = Field(min_length=3)
    author: str = Field(min_length=3)
    description: str = Field(min_length=10)
    rating: int = Field(gt=0, lt=6)
    published_date: int 
    
    model_config = {
        "json_schema_extra":{
            "example": {
                "id": 1,
                "title": "Book1",
                "author": "Author1",
                "description": "This is a book",
                "rating": 5,
                "published_date": 2019
            }
        }
    }

BOOKS = [
    Book(1,'Dev ops' , 'Mukhtar Ahmed','Its nice book',5,2019),
    Book(2,'Python' , 'Mukhtar Ahmed','Its nice book',4,2020),
    Book(3,'Java' , 'Mukhtar Ahmed','Its nice book',3,2019),
    Book(3,'c++' , 'Awais','Average',5,2015),
]

@app.get('/books', status_code=status.HTTP_200_OK)
def read_books():
    return {
        'message': 'Sucess',
        'total': len(BOOKS),
        'data': BOOKS
    }
    
@app.post("/books/create-book" , status_code=status.HTTP_201_CREATED)
def create_book(book : BookIn):
    BOOKS.append(find_book_id(Book(**book.model_dump())))
    return {
        'message': 'Sucess',
        'total': len(BOOKS),
        'data': BOOKS
    }
    
# @app.get('/books/{book_published_date}', status_code=status.HTTP_200_OK)
# def get_books_by_published_date(book_published_date:int=Path(gt=1999, lt=2026)):
#     return_book = []
#     for book in BOOKS:
#         if book.published_date == book_published_date:
#             return_book.append(book)
#     return {
#         'message': 'Sucess',
#         'total': len(return_book),
#         'data': return_book
#     }
    
@app.get('/books/{book_id}', status_code=status.HTTP_200_OK)
def read_book(book_id:int):
    for book in BOOKS:
        if book.id == book_id:
            return {
                'message': 'Sucess',
                'data': book
                }
    return {'message': 'Book not found', 'status_code':HTTPException(status_code=400, detail='Not Found')}



@app.get("/books/")
async def bookByRating(book_by_rating: int):
    books = []
    for book in BOOKS:
        if book.rating == book_by_rating:
            books.append(book)
    return {
        'message':'Sucess',
        'total':len(books),
        'data':books
    }



@app.put("/books/update_book")
async def update_book(book: BookIn):
    book_changed = False
    for i in range(len(BOOKS)):
        if BOOKS[i] == book.id:
            BOOKS[i] = book
            book_changed = True
            return {
                'message': 'Sucess',
                'data': BOOKS[i]
                }
        return {'message': 'Book not found'}
    

    


















    
def find_book_id(book: Book):
    if(len(BOOKS) > 0):
        book.id = BOOKS[-1].id + 1
    else:
        book.id = 1
        
    return book