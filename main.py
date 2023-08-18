from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests


MY_API_KEY = '9127abe2f5d80b6402b3c4547f88e0f0'
API_END_POINT = f'https://api.themoviedb.org/3/search/movie?api_key={MY_API_KEY}&language=en-US&query=<<>>page=1&include_adult=true'
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movies_collection.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Bootstrap(app)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.String(250), nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)

    # Optional: this will allow each book object to be identified by its title when printed.
    def __repr__(self):
        return f'<Book {self.title}>'


class UpdateForm(FlaskForm):
    rating = StringField(label='Your Rating Out of 10 e.g. 7.5')
    review = StringField(label='Your Review')
    submit = SubmitField(label="Done")


class AddForm(FlaskForm):
    title = StringField(label='Movie Title', validators=[DataRequired()])
    submit = SubmitField(label="Add Movie")


with app.app_context():
    db.create_all()


# new_movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )
# db.session.add(new_movie)
# db.session.commit()

@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating.desc()).all()
    i = 0
    for movie in all_movies:
        movie.ranking = len(all_movies) - i
        i += 1
        db.session.commit()
    return render_template("index.html", movies=all_movies)


@app.route("/edit", methods=["GET", "POST"])
def update():
    update_form = UpdateForm()
    movie_id = request.args.get("id_no")
    movie = Movie.query.get(movie_id)
    if update_form.validate_on_submit():
        movie.rating = float(update_form.rating.data)
        movie.review = update_form.review.data
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('edit.html', form=update_form)


@app.route("/delete", methods=["GET", "POST"])
def delete():
    movie_id = request.args.get("id_no")
    movie = Movie.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/add", methods=["GET", "POST"])
def add():
    add_form = AddForm()
    if add_form.validate_on_submit():
        headers = {'Accept': 'application/json'}
        response = requests.get(url=f'https://api.themoviedb.org/3/search/movie?api_key={MY_API_KEY}&query={add_form.title.data}', headers=headers)
        response.raise_for_status()
        return render_template('select.html', options=response.json()['results'])
    return render_template('add.html', form=add_form)


@app.route("/find", methods=["GET", "POST"])
def update_db():
    m_id = request.args.get('movie_id')
    print(m_id)
    response_json = (requests.get(url=f'https://api.themoviedb.org/3/movie/{m_id}?api_key={MY_API_KEY}&language=en-US')).json()
    movie_title = response_json['original_title']
    img_url = f"https://image.tmdb.org/t/p/original{response_json['poster_path']}"
    year = response_json['release_date']
    description = response_json['overview']
    new_movie = Movie(title=movie_title, img_url=img_url, year=year, description=description)
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for('update', id_no=new_movie.id))


if __name__ == '__main__':
    app.run(debug=True)
