from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, ValidationError
from wtforms.validators import DataRequired
import requests


MY_API_KEY = "78747f340d4fb207dc728f7b7a4ba360"
URL = "https://api.themoviedb.org/3/authentication/token/new"
MY_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI3ODc0N2YzNDBkNGZiMjA3ZGM3MjhmN2I3YTRiYTM2MCIsInN1YiI6IjYyYmRkNWVkN2VmMzgxMjc2N2YzMmY4YSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.uxU86sZLpzT39rIPUahQmhYwwpDHhcyQtzwu4LWSXAM"
header = {
    "Authorization": f"Bearer {MY_TOKEN}",
    "Content-Type": "application/json;charset=utf-8"
}


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)


def url_check(form, field):
    """Takes the FlaskForm object and checks for any 'https' tag in Field Data.
    If not, raises Validation Error"""
    text = field.data
    if text[:5] != "https":
        raise ValidationError('URL has to has "https" tag!')


# CREATE A DATABASE AND ADD A TABLE THAT CALLED "Movie" BY USING SQLALCHEMY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movie-collection.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(1000000), nullable=False)
    rating = db.Column(db.Float)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String(250))
    img_url = db.Column(db.String(500), nullable=False)


db.create_all()


# CREATE FLASK-FORM FOR ADD PAGE
class MovieForm(FlaskForm):
    """Inherits with FlaskForm class, creates Input Fields and Button For Submit"""
    title = StringField('Movie Title:', validators=[DataRequired()])
    submit = SubmitField('Done')


# CREATE FLASK-FORM FOR EDIT PAGE
class EditForm(FlaskForm):
    """Inherits with FlaskForm class, creates Editing Fields and Button For Submit"""
    rating = FloatField('Your Raiting Out of 10 e.g. 7.5:', validators=[DataRequired()])
    review = StringField('Your Review:', validators=[DataRequired()])
    submit = SubmitField('Done')


@app.route("/")
def home():
    # This line creates a list of all the movies sorted by rating
    all_movies = Movie.query.order_by(Movie.rating).all()
    # This line loops through all the movies
    for i in range(len(all_movies)):
        # This line gives each movie a new ranking reversed from their order in all_movies
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", all_movies=all_movies)


@app.route("/add", methods=["GET", "POST"])
def add():
    add_form = MovieForm()
    if add_form.validate_on_submit():
        new_title = add_form.title.data
        response = requests.get(URL, headers=header, params=MY_API_KEY)
        request_token = response.json()['request_token']
        search_json = {
            "api_key": request_token,
            "query": f"{new_title}"
        }
        response2 = requests.get("https://api.themoviedb.org/3/search/movie", headers=header, params=search_json)
        results = response2.json()['results']
        return render_template("select.html", results=results)
    return render_template("add.html", form=add_form)


@app.route("/selected/<selected_movie_id>")
def selected(selected_movie_id):
    response = requests.get(URL, headers=header, params=MY_API_KEY)
    request_token = response.json()['request_token']
    params = {
        "api_key": request_token
    }
    response3 = requests.get(f"https://api.themoviedb.org/3/movie/{selected_movie_id}", headers=header, params=params)
    new_movie_data = response3.json()
    new_movie = Movie(title=new_movie_data['title'], description=new_movie_data['overview'],
                      rating=new_movie_data['vote_average'], year=new_movie_data['release_date'][:4],
                      ranking="", review="",
                      img_url=f"https://image.tmdb.org/t/p/original/"
                              f"{new_movie_data['poster_path']}")
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/edit/<movie_id>", methods=["GET", "POST"])
def edit(movie_id):
    editform = EditForm()
    clicked_id = int(movie_id)
    if editform.validate_on_submit():
        movie_to_update = Movie.query.all()[clicked_id-1]
        movie_to_update.rating = editform.rating.data
        movie_to_update.review = editform.review.data
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit.html", edit_form=editform)


@app.route("/delete/<movie_id>")
def delete(movie_id):
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
