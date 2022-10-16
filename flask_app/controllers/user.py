from datetime import datetime
from flask import render_template, request, redirect, session, flash, url_for
from flask_app import app
from flask_app.models import user, event
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

@app.route("/test_data")
def main():
    return redirect("/test")

@app.route('/test')
def test():
    all_users = user.User.get_all_users()
    all_events = event.Event.get_all_events()
    user_array = [user.User(x) for x in all_users]
    events_array = []

    ## This changes the *timedelta* to a *time* so we can format it
    for x in all_events:
        x["time_start"] = (datetime.min + x["time_start"]).time()
        x["time_end"] = (datetime.min + x["time_end"]).time()
        events_array.append(event.Event(x))

    return render_template("index.html", user_array=user_array, events_array=events_array)



## Hidden routes
@app.route("/user/new/create", methods=["POST"])
def register():

    data = {
        "first_name": request.form["first_name"],
        "last_name": request.form["last_name"],
        "email": request.form["email"],
        "password": request.form["password"],
    }

    if request.form["confirm_password"] != request.form["password"]:
        flash("Passwords do not match")
        return redirect("/")
    if user.User.check_if_email_in_system(data):
        flash("Email already taken")
        return redirect("/")

    hash_pass = bcrypt.generate_password_hash(request.form["password"])
    data["password"] = hash_pass
    session["user_id"] = user.User.save_user(data)
    # we might need two separate pages for signed in vs non signed in people or just
    return redirect("/dashboard")

@app.route("/user/sign_in")
def sign_in():
    data = {
        'email':request.form['email'],
    }
    user_in_db = user.User.get_user_by_email(data)
    
    if not user_in_db:
        flash('Invalid Email/Password', 'sign_in')
        return redirect('/')
    if not bcrypt.check_password_hash(user_in_db.password, request.form['password']):
        flash('Invalid Email/Password', 'sign_in')
        return redirect('/')
    session['user_id'] = user_in_db.id
    return redirect('/dashboard')


@app.route('/signout')
def signout():
    session.clear()
    return redirect('/')

