from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

SEARCH_ENDPOINT = 'https://api.themoviedb.org/3/search/movie'
DETAIL_ENDPOINT = 'https://api.themoviedb.org/3/movie/'
BASE_IMG_URL = 'https://image.tmdb.org/t/p/original'
API_KEY = 'da74dfb66163e383702e2a49eb544512'

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

db = SQLAlchemy()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///moviesite.db"
db.init_app(app)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.String(10), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Float)
    ranking = db.Column(db.Integer)
    review = db.Column(db.String(250))
    img_url = db.Column(db.String(250), nullable=False)

class Rating(FlaskForm):
    rating = StringField('Your Rating Out Of 10 eg. 7.5', validators=[DataRequired()])
    review = StringField('What is your review?', validators=[DataRequired()])
    submit = SubmitField('Done')

class AddMovie(FlaskForm):
    title = StringField('Movie Title', validators=[DataRequired()])
    submit = SubmitField('Add Movie')

def get_movies(title):
    param = {
        'api_key': API_KEY,
        'query': title,
    }
    response = requests.get(url=SEARCH_ENDPOINT, params=param)
    return response.json()['results']

def get_movie_details(id):
    param = {
        'api_key': API_KEY,
    }
    response = requests.get(url=DETAIL_ENDPOINT+str(id), params=param)
    return response.json()


@app.route("/")
def home():
    # movies = Movie.query.all()
    movies = Movie.query.order_by(Movie.rating.desc()).all()
    for index in range(len(movies)):
        movies[index].ranking = index+1

    db.session.commit()

    return render_template("index.html", movies=movies)

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    form = Rating()
    if form.validate_on_submit():
        id = request.args.get('id')
        new_rating = Movie.query.filter_by(id=id).first()
        new_rating.rating = request.form['rating']
        new_rating.review = request.form['review']
        db.session.add(new_rating)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', form=form)

@app.route('/delete')
def delete():
    id =request.args.get('id')
    unwanted_movie = Movie.query.filter_by(id=id).first()
    db.session.delete(unwanted_movie)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/add', methods=['GET', 'POST'])
def add():
    form = AddMovie()
    if form.validate_on_submit():
        movie_title = request.form['title']
        movie_list = get_movies(title=movie_title)
        return render_template('select.html', movies=movie_list)

    return render_template('add.html', form=form)


@app.route('/find')
def find():
    movie_id = request.args.get('id')
    movie_detail = get_movie_details(movie_id)
    new_movie = Movie(
        title = movie_detail['original_title'],
        img_url = BASE_IMG_URL + movie_detail['backdrop_path'],
        year = movie_detail['release_date'][0:4],
        description = movie_detail['overview'],
        )
    db.session.add(new_movie)
    db.session.commit()

    return redirect(url_for('edit', id=new_movie))


if __name__ == '__main__':
    # new_movie = Movie(
    #     title="Phone Booth",
    #     year=2002,
    #     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
    #     rating=7.3,
    #     ranking=10,
    #     review="My favourite character was the caller.",
    #     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
    # )

    # with app.app_context():
    #     db.create_all()
    #     db.session.add(new_movie)
    #     db.session.commit()

    app.run(debug=True)
