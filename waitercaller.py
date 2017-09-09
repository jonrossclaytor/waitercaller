from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.login import login_required
from flask.ext.login import login_user
from flask.ext.login import logout_user
from flask import render_template
from flask import redirect
from flask import request
from flask import url_for

# user-defined libraries
from mockdbhelper import MockDBHelper as DBHelper
from user import User
from passwordhelper import PasswordHelper

DB = DBHelper()
PH = PasswordHelper()

app = Flask(__name__)
login_manager = LoginManager(app)
app.secret_key = 'cdqNmNWPjebu2ItUiPJID2Aigz6Fr1uWtkDkN8NC6UhUnVkfQJyUliAZfWwSNcb1+fFgxPygcXQ6aFZ/LUuR59Gq3ahcenUEEa8'

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    stored_user = DB.get_user(email)
    if stored_user and PH.validate_password(password, stored_user['salt'], stored_user['hashed']):
        user = User(email)
        login_user(user, remember=True) # handles authentication
        return redirect(url_for('account')) # this is better than but similar to 'return account()'
    return home()

@login_manager.user_loader # function to handle users who are already logged in and have a cookie assigned by login_user
def load_user(user_id): # user_id variable comes from the cookie
    user_password = DB.get_user(user_id)
    if user_password:
        return User(user_id)

@app.route("/register", methods=['POST'])
def register():
    email = request.form.get('email')
    pw1 = request.form.get('password')
    pw2 = request.form.get('password2')
    if not pw1 == pw2:
        return redirect(url_for('home'))
    if DB.get_user(email):
        return redirect(url_for('home'))
    salt = PH.get_salt()
    hashed = PH.get_hash(pw1 + salt)
    DB.add_user(email, salt, hashed)
    return redirect(url_for('home'))

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))
        
@app.route("/account")
@login_required
def account():
    return "You are logged in."

if __name__ == "__main__":
    app.run(port=5000, debug=True)
