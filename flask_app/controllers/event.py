from flask import render_template, request, redirect, session, flash, url_for
from flask_app import app
from flask_app.models import user, event



### Hidden Routes

# create
@app.route("/events/new/create", methods=["POST"])
def create_event():
    if "user_id" not in session:
        return redirect("/")
    data = {
        "name": request.form["name"],
        "date": request.form["date"],
        "time_start": request.form["time_start"],
        "time_end": request.form["time_end"],
        "address": request.form["address"],
        "details": request.form["details"],
        "options": request.form["options"],
        "plus_one": request.form["plus_one"],
        "user_id": session["user_id"]
    }

    # validate event not currently working

    # if not event.Event.validate_event(data):
    #     return redirect("/events/new/create_one")

    event.Event.create(data)
    return redirect("/dashboard")

# edit/update
@app.route("/events/update/<int:id>", methods=["POST"])
def edit_event(id):
    if "user_id" not in session:
        return redirect("/")
    data = {
        "id":id,
        'name': request.form['name'],
        'date': request.form['date'],
        'time_start': request.form['time_start'],
        'time_end': request.form['time_end'],
        'address': request.form['address'],
        'options': request.form['options'],
        'plus_one': request.form['plus_one'],
    }

    # validate event not currently working
    # if not event.Event.validate_event(data):
    #     return redirect(f"/events/edit/{id}")

    event.Event.update(data)
    return redirect("/dashboard")

# delete
@app.route("/events/delete/<int:id>")
def delete_event(id):
    if "user_id" not in session:
        return redirect('/')
    data = {
        'id':id
    }
    event.Event.delete(data)
    return redirect("/dashboard")


# send email invite
app.route("/events/view/<int:id>/invite")
def invite_one():
    pass

# visible routes

# dashboard/viewall
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/")
    data = {
        "id" : session["user_id"]
    }
    user_data=user.User.get_user_by_id(data)
    all_events=event.Event.get_all_events()
    return render_template("dashboard.html", this_user=user_data, all_events=all_events)

# create
@app.route("/events/new/create_one")
def create_one():
    if "user_id" not in session:
        return redirect("/")
    return render_template("create_event.html")

# edit/update
@app.route("/events/edit/<int:id>")
def edit_one(id):
    if "user_id" not in session:
        return redirect("/")
    event_data={
        "id":id
    }
    this_event=event.Event.get_event_by_id(event_data)
    return render_template("edit_one_event.html", this_event=this_event)

# view one
@app.route("/events/view/<int:id>")
def view_one(id):
    if "user_id" not in session:
        return redirect(f"/non_user/events/view/{id}")
    event_data={
        "id":id
    }
    user_data={
        "id":session["user_id"]
    }
    user_info = user.User.get_user_by_id(user_data)
    one_event=event.Event.get_event_by_id(event_data)
    return render_template("show_one_event_user.html", one_event=one_event, user_info=user_info)

@app.route("/non_user/events/view/<int:id>")
def view_one_non_user(id):
    if "user_id" in session:
        return redirect(f"/events/view/{id}")
    event_data={
        "id":id
    }
    one_event=event.Event.get_event_by_id(event_data)
    print(one_event)
    return render_template("show_one_event_non_user.html", one_event=one_event)

