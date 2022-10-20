from datetime import datetime
from flask import render_template, request, redirect, session, flash, url_for
from flask_app import app
from flask_app.models import user, event
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

# view all users and data/tester
@app.route("/test_data")
def test_data():
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

    return render_template("tester.html", user_array=user_array, events_array=events_array)

# Login/registration page
@app.route('/')
def index():
    if "user_id" in session:
        return redirect("/dashboard")
    return render_template('index.html')

# create user
@app.route("/user/new/create", methods=["POST"])
def register():

    data = {
        "first_name": request.form["first_name"],
        "last_name": request.form["last_name"],
        "email": request.form["email"],
        "password": request.form["password"],
    }

    if not user.User.validate_user(request.form):
        return redirect("/")
    if user.User.get_user_by_email(data):
        flash("Email already in system", "register")
        return redirect('/')

    hash_pass = bcrypt.generate_password_hash(request.form["password"])
    data["password"] = hash_pass
    session["user_id"] = user.User.save(data)
    return redirect("/dashboard")

# sign in
@app.route("/user/sign_in", methods=["POST"])
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

#created separate table in "/dashboard" to display user's own events

# view your events
# @app.route("/user/your_events")
# def your_events():
#     if "user_id" not in session:
#         return redirect('/')
    
#     user_data = {
#         "id":session['user_id']
#     }
#     event_data = {
#         "user_id":user_data['id']
#     }
#     user_data = user.User.get_user_by_id(user_data)
#     events = user.User.get_one_user_with_events(event_data)
#     return render_template('user_events.html', user_data=user_data, events=events)

@app.route('/signout')
def signout():
    session.clear()
    return redirect('/')