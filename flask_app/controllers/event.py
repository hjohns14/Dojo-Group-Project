from flask import render_template, request, redirect, session, flash, url_for
from flask_app import app
from flask_app.models import user, event



### Hidden Routes
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
