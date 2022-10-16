from flask import render_template, request, redirect, session, flash, url_for
from flask_app import app
from flask_app.models import user, event



### Hidden Routes

# create
@app.route("/events/new/create", methods=["POST"])
def create_event():
    data = {
        "name": request.form["name"],
        "date": request.form["date"],
        "time_start": request.form["time_start"],
        "time_end": request.form["time_end"],
        "address": request.form["address"],
        "details": request.form["details"],
        "options": request.form["options"],
        "plus_one": request.form["plus_one"],
        "user_id": request.form["user_id"]
    }

    new_event = event.Event.create(data)
    

    return redirect("/")

# update
@app.route("/events/update/<int:id>", methods=["POST"])
def edit_event():
    pass

# delete
@app.route("events/delete/<int:id>")
def delete_event():
    pass

# send email invite
app.route("/events/view/<int:id>/invite")
def invite_one():
    pass




# visible routes

# dashboard/viewall
@app.route("/")
def index():
    pass

# create
@app.route("/events/new/create_one")
def create_one():
    pass

# edit
@app.route("/events/edit/<int:id>")
def edit_one():
    pass

# view one
@app.route("/events/view/<int:id>")
def view_one():
    pass
