from flask import Flask, jsonify, request
from flask_restx import Api, Resource
from pydantic import BaseModel

from server.instance import server, db
from server.models.books import model_books
from server.sqlite import Books

app, api = server.app, server.api

booksNS = api.namespace('books', description='Books operations')

@booksNS.route('/', endpoint='Books')
class BookList(Resource):
    @booksNS.doc('list_books')
    @booksNS.marshal_list_with(model_books)
    def get(self):
        books = Books.query.all()
    
        return [book.to_dict() for book in books]
    
    @booksNS.doc('create_book')
    @booksNS.expect(model_books)
    @booksNS.response(400, 'Book already exists')
    def post(self):
        data_request = {
            "title": request.json['title'],
            "author": request.json['author'],
            "description": request.json['description'],
        }

        try:
            validated = PydanticBook(**data_request)
        except Exception as error:
            return error.errors(), 422
        
        book_existed = Books.query.filter_by(title=validated.title).first()
        if book_existed:
            return {'error': 'Book already exists!'}, 400
        
        new_book = Books(
            title=validated.title,
            author=validated.author,
            description=validated.description
        )
        
        db.session.add(new_book)
        db.session.commit()

        return new_book.to_dict(), 201
    
@booksNS.route('/<int:id>')
@booksNS.response(404, 'Book not found')
@booksNS.param('id', 'The book identifier')
class Book(Resource):
    @booksNS.doc('get_book')
    def get(self, id):
        book_existed = Books.query.get(id)
        if not book_existed:
            return {'error': 'Book does not exist!'}, 404
    
        return book_existed.to_dict(), 200

    @booksNS.doc('delete_book')
    @booksNS.response(204, 'Book deleted')
    def delete(self, id):
        book_existed = Books.query.get(id)
        if not book_existed:
            return {'error': 'Book does not exist!'}, 404
    
        db.session.delete(book_existed)
        db.session.commit()

        return '', 204

    @booksNS.doc('update_book')
    @booksNS.expect(model_books)
    def put(self, id):
        book_existed = Books.query.get(id)
        if not book_existed:
            return {'error': 'Book does not exist!'}, 404
    
        data = request.get_json()

        for key, value in data.items():
            setattr(book_existed, key, value)

        db.session.commit()

        return book_existed.to_dict(), 200
    
class PydanticBook(BaseModel):
    title: str
    author: str
    description: str
