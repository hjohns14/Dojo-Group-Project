from datetime import datetime
from flask import render_template, request, redirect, session, flash, url_for
from flask_app import app
from flask_app.models import user, event
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

@app.route("/")
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
    #Validations Here

    hash_pass = bcrypt.generate_password_hash(request.form["password"])

    data = {
        "first_name": request.form['first_name'],
        "last_name": request.form['last_name'],
        "email": request.form['email'],
        "password": hash_pass,
    }

    user_info = user.User.save(data)
    print(user_info)
    return redirect("/")

@app.route("/user/signout")
def singout():
    session.clear()
    return redirect('/')


#visible
@app.route("/user/new/create_one_user")
def create_one_user():
    pass