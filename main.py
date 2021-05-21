from flask import Flask, render_template, redirect, url_for
import numpy as np
from PIL import Image
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
import os
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisappisatest!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/photo.db'
db = SQLAlchemy(app)


class Photodb(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(250), nullable=False)


class PhotoForm(FlaskForm):
    url = StringField('image', validators=[DataRequired()], render_kw={'style': 'width: 50ch'})


db.create_all()


# ---------------
def extract_rgb(url):
    im = Image.open(requests.get(url, stream=True).raw)
    img = np.asarray(im)
    new_array = np.ravel(img, order='C')
    all_new_array = np.reshape(new_array, (-1, 3))
    unique, counts = np.unique(all_new_array, axis=0, return_counts=True)
    max_10 = np.sort(counts)[::-1][:10]

    index_list = []
    for i in max_10:
        index = np.where(counts == i)
        index_list.append(index)

    rgb_arr = []
    for i in index_list:
        rgb_arr.append(unique[i])
    return rgb_arr


# ---------------


@app.route('/', methods=['GET', 'POST'])
def home():
    form = PhotoForm()
    img_url = Photodb.query.all()
    if form.validate_on_submit():
        print("success path")
        f = form.url.data
        new_session = Photodb(url=f)
        db.session.add(new_session)
        rgb_array = extract_rgb(f)
        return redirect(url_for('home'))

    return render_template('index.html', form=form, img_url=img_url, rgb_array=rgb_array)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)




