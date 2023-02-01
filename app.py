# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
api = Api(app)

movies_ns = api.namespace('movies')
directors_ns = api.namespace('directors')
genres_ns = api.namespace('genres')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


class DirectorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class GenreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)
director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)
genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


@movies_ns.route('/')
class MoviesView(Resource):
    def get(self):
        """
        Позволяет получить все фильмы
        """
        genre_id = request.values.get('genre_id')
        director_id = request.values.get('director_id')

        with app.app_context():
            with db.session.begin():

                if genre_id and director_id:
                    movies = db.session.query(Movie).filter(Movie.genre_id == genre_id,
                                                            Movie.director_id == director_id).all()
                elif genre_id:
                    movies = db.session.query(Movie).filter(Movie.genre_id == genre_id).all()
                elif director_id:
                    movies = db.session.query(Movie).filter(Movie.director_id == director_id).all()
                else:
                    movies = db.session.query(Movie).all()

                if movies:
                    movies_json = movies_schema.dump(movies)
                    return movies_json, 200

                else:
                    return '', 404

    def post(self):
        """
        Позволяет добавить новый фильм
        :return:
        """
        new_movie_json = request.json
        new_movie_dict = movie_schema.load(new_movie_json)
        new_movie = Movie(**new_movie_dict)

        with app.app_context():
            with db.session.begin():
                db.session.add(new_movie)
                db.session.commit()

        return '', 204


@movies_ns.route('/<int:id_>')
class MovieView(Resource):
    def get(self, id_):
        """
        Позволяет получить фильм по его id_
        :param id_: id фильма
        """
        with app.app_context():
            with db.session.begin():
                movie = db.session.query(Movie).get(id_)

                if movie:
                    movie_json = movie_schema.dump(movie)
                    return movie_json, 200

                else:
                    return '', 404

    def put(self, id_):
        """
        Позволяет полностью обновить информацию о фильме
        :param id_: id фильма
        """
        with app.app_context():
            with db.session.begin():
                movie = db.session.query(Movie).get(id_)

                if movie:
                    movie_dict = movie_schema.load(request.json)
                    movie.title = movie_dict.get('title')
                    movie.description = movie_dict.get('description')
                    movie.trailer = movie_dict.get('trailer')
                    movie.year = movie_dict.get('year')
                    movie.rating = movie_dict.get('rating')
                    movie.genre_id = movie_dict.get('genre_id')
                    movie.director_id = movie_dict.get('director_id')

                    db.session.add(movie)
                    db.session.commit()
                    return '', 204

                else:
                    return '', 404

    def patch(self, id_):
        """
        Позволяет частично обновить информацию о фильме
        :param id_: id фильма
        """
        with app.app_context():
            with db.session.begin():
                movie = db.session.query(Movie).get(id_)

                if movie:
                    movie_dict = movie_schema.load(request.json)
                    if 'title' in movie_dict:
                        movie.title = movie_dict.get('title')
                    if 'description' in movie_dict:
                        movie.description = movie_dict.get('description')
                    if 'trailer' in movie_dict:
                        movie.trailer = movie_dict.get('trailer')
                    if 'year' in movie_dict:
                        movie.year = movie_dict.get('year')
                    if 'rating' in movie_dict:
                        movie.rating = movie_dict.get('rating')
                    if 'genre_id' in movie_dict:
                        movie.genre_id = movie_dict.get('genre_id')
                    if 'director_id' in movie_dict:
                        movie.director_id = movie_dict.get('director_id')

                    db.session.add(movie)
                    db.session.commit()
                    return '', 204

                else:
                    return '', 404

    def delete(self, id_):
        """
        Позволяет удалить фильма
        :param id_: id фильма
        """
        with app.app_context():
            with db.session.begin():
                movie = db.session.query(Movie).get(id_)

                if movie:
                    db.session.delete(movie)
                    return '', 204

                else:
                    return '', 404


@directors_ns.route('/')
class DirectorsView(Resource):
    def get(self):
        """
        Позволяет получить всех режиссеров
        """
        with app.app_context():
            with db.session.begin():
                directors = db.session.query(Director).all()
                directors_json = directors_schema.dump(directors)

        return directors_json, 200

    def post(self):
        """
        Позволяет добавить нового режиссера
        """
        new_director_json = request.json
        with app.app_context():
            new_director_dict = director_schema.load(new_director_json)
            new_director = Director(**new_director_dict)

            with db.session.begin():
                db.session.add(new_director)
                db.session.commit()

        return '', 204


@directors_ns.route('/<int:id_>')
class DirectorView(Resource):
    def get(self, id_):
        '''
        Позволяет получить режиссера по его id
        :param id_: id режиссера
        '''
        with app.app_context():
            with db.session.begin():
                director = db.session.query(Director).get(id_)

                if director:
                    director_json = director_schema.dump(director)
                    return director_json, 200

                else:
                    return '', 404

    def put(self, id_):
        """
        Позволяет поменять всю информацию о режиссере
        :param id_: id режиссера
        """
        with app.app_context():
            with db.session.begin():
                director = db.session.query(Director).get(id_)

                if director:
                    director_json = director_schema.load(request.json)
                    director.name = director_json.get('name')
                    db.session.add(director)
                    db.session.commit()
                    return '', 204

                else:
                    return '', 404

    def delete(self, id_):
        """
        Позволяет удалить режиссера из БД
        :param id_: id режиссера
        """
        with app.app_context():
            with db.session.begin():
                director = db.session.query(Director).get(id_)

                if director:
                    db.session.delete(director)
                    return '', 204

                else:
                    return '', 404


@genres_ns.route('/')
class GenresView(Resource):
    def get(self):
        """
        Позволяет получить все жанры
        """
        with app.app_context():
            with db.session.begin():
                genres = db.session.query(Genre).all()
                genres_json = genres_schema.dump(genres)

        return genres_json, 200

    def post(self):
        """
        Позволяет добавить новый жанр
        """
        new_genre_json = request.json
        with app.app_context():
            new_genre_dict = genre_schema.load(new_genre_json)
            new_genre = Genre(**new_genre_dict)

            with db.session.begin():
                db.session.add(new_genre)
                db.session.commit()

        return '', 204


@genres_ns.route('/<int:id_>')
class GenreView(Resource):
    def get(self, id_):
        """
        Позволяет получить жанр по его id
        :param id_: id жанра
        """
        with app.app_context():
            with db.session.begin():
                genre = db.session.query(Genre).get(id_)

                if genre:
                    genre_json = genre_schema.dump(genre)
                    return genre_json, 200

                else:
                    return '', 404

    def put(self, id_):
        """
        Позволяет поменять информацию о жанре
        :param id_: id жанра
        """
        with app.app_context():
            with db.session.begin():
                genre = db.session.query(Genre).get(id_)

                if genre:
                    genre_json = genre_schema.load(request.json)
                    genre.name = genre_json.get('name')
                    db.session.add(genre)
                    db.session.commit()
                    return '', 204

                else:
                    return '', 404

    def delete(self, id_):
        """
        Позволяет удалить жанр
        :param id_: id жанрам
        """
        with app.app_context():
            with db.session.begin():
                genre = db.session.query(Genre).get(id_)

                if genre:
                    db.session.delete(genre)
                    return '', 204

                else:
                    return '', 404


if __name__ == '__main__':
    app.run(debug=True)
