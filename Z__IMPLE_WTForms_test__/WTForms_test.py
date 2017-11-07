from flask import Flask,render_template,url_for,redirect
from flask_wtf import FlaskForm
from wtforms import TextField
from wtforms.validators import Required
import socket

app=Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

class MyForm(FlaskForm):
    name = TextField('name', validators=[Required()])

class MyForm2(FlaskForm):
    name = TextField('name', validators=[Required()])

@app.route('/')
def index():
    return 'index'

@app.route('/success',methods=['GET','POST'])
def success():
    form=MyForm2()
    if form.validate_on_submit():
        return redirect(url_for('index'))
    return render_template('success.html', form=form)

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    form = MyForm()
    if form.validate_on_submit():
        return redirect(url_for('success'))
    return render_template('submit.html', form=form)

app.run(host='localhost',port=1234,debug=True)
