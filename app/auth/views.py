from flask import render_template,flash, request, url_for, redirect,make_response,abort
from . import auth
from .forms import LoginForm,RegistrationForm
from ..models import User,db
import time
from flask_login import login_user,logout_user

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user= User.query.fiflter_by(name= form.username.data,password= form.password.data)
        flash('ok-.-')
        if user  is not None:
            login_user(user)
            return redirect(url_for('main.index'))

    return render_template('login.html',form=form, title='Login-.-')

@auth.route('/user/<int:user_id>/')
def user(user_id):
    return 'user_id %d' % user_id

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/register', methods=['GET','POST'])
def register():
    form= RegistrationForm()
    if form.validate_on_submit:
        time.sleep(5)
        user=User(name=form.username.data, password=form.password.data)
        db.session.add(user)
        #db.session.submit()
        #return redirect(url_for('auth.login'))
    return render_template('register.html',title='Register',form=form)