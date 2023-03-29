from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired, NumberRange
import requests

db = SQLAlchemy()
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Movie"
db.init_app(app)
api_key = "f06638266651db78c7bfa679f5cb0e54&query"


class MovieData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String, nullable=False)
    img_url = db.Column(db.String, nullable=False)


@app.route("/")
def home():
    movie = db.session.query(MovieData).all()

    for n in range(len(movie)):
        for one_movie in range(len(movie) - 1):
            if movie[one_movie].rating > movie[one_movie + 1].rating:
                movie[one_movie], movie[one_movie + 1] = movie[one_movie + 1], movie[one_movie]
    movies_num = len(movie)
    return render_template("index.html", movie=movie, num_movies = movies_num)


@app.route('/edit/id/<int:id_num>', methods=['POST', 'GET'])
def edit(id_num):
    class edit_move(FlaskForm):
        rating = FloatField("rating", validators=[
            NumberRange(min=0,
                        max=10,
                        message="Please write a number between 0 and 10")
        ])
        review = StringField("review", validators=[DataRequired()])
        Done = SubmitField()

    if request.method == 'POST':
        to_edit = MovieData.query.get(id_num)
        to_edit.rating = request.form['rating']
        to_edit.review = request.form['review']
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", form=edit_move(), id=id_num)


@app.route("/delete/<int:num>")
def delte(num):
    book = MovieData.query.get(num)
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/add_movie", methods=['POST', 'GET'])
def add():
    class FindMovie(FlaskForm):
        name = StringField("movie_name", validators=[DataRequired()])
        add = SubmitField()

    if request.method == 'POST':
        req = requests.get(
            f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query=" + request.form[
                'name'])
        data = req.json()["results"]
        results = req.json()["total_results"]
        return render_template('select.html', data=data, results_num=results)
    return render_template("add.html", form=FindMovie())


@app.route('/add/<movie_id>')
def add_movie(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&query&language=en-US"
    movie = requests.get(url).json()
    title = movie['original_title']
    description = movie['overview']
    release_date = movie['release_date'].split('-')[0]
    img = "https://image.tmdb.org/t/p/w500" + movie['poster_path']
    movie = MovieData(
        id=movie['id'],
        title=title,
        year=release_date,
        description=description,
        rating=0,
        ranking=0,
        review='',
        img_url=img
    )
    db.session.add(movie)
    db.session.commit()
    return redirect(url_for('edit', id_num=movie_id))


if __name__ == '__main__':
    app.run(debug=True)
