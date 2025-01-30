from fastapi import FastAPI, Body
app= FastAPI()

Books = [
    {'title':'Title 1', 'author':'Author 1', 'category':'Science'},
    {'title':'Title 2', 'author':'Author 2', 'category':'History'},
    {'title':'Title 3', 'author':'Author 3', 'category':'Science'},
    {'title':'Title 4', 'author':'Author 4', 'category':'History'},
    {'title':'Title 5', 'author':'Author 5', 'category':'Science'},
]

@app.get('/books')
async def read_all_books():
    return {'message': 'Sucess',
            'total':len(Books),
            'data':Books
            }
    
@app.get('/books/')
async def read_book_by_category(category: str):
    category_book = []
    for book in Books:
        if book['category'].casefold() == category.casefold():
            category_book.append(book)
    return {'message': 'Sucess',
            'total':len(category_book),
            'data':category_book
            }

@app.get('/books/{book_title}')
async def read_book(book_title : str):
    for book in Books:
        if book['title'].casefold() == book_title.casefold():
            return {'message': 'Sucess',
                    'data': book
                    }
    return {'message': 'Book not found'}

@app.get('/books/{auth_name}/')
async def filter_book_by_author_category(auth_name: str,category:str):
    filtered_book = []
    for book in Books:
        if book['author'].casefold() == auth_name.casefold() and book['category'].casefold() == category.casefold():
            filtered_book.append(book)
            
    return {
        'message':'sucess',
        'total': len(filtered_book),
        'data': filtered_book
    }

@app.post('/books/create_book')
async def create_book(new_book= Body()):
    Books.append(new_book)
    return {
        'message':'sucess',
        'total': len(Books),
        'data': Books
    }
    
@app.put('/books/update_book')
async def update_book(book_info=Body()):
    for book in Books:
        if book['author'].casefold() == book_info['author'].casefold():
            book['title'] = book_info['title']
            book['category'] = book_info['category']
    return {
        'message':'sucess',
        'total': len(Books),
        'data': Books
    }
    
@app.delete('/books/delete_book/{book_title}')
async def delete_book(book_title: str):
    for book in Books:
        if book['title'].casefold() == book_title.casefold():
            Books.remove(book)
            return {'message':'sucess',
                    'total': len(Books),
                    'data': Books
                    }
            return {'message':'Book not found'}
    
    