from flask import render_template, request, redirect, session, flash, url_for
from flask_app import app
from flask_app.models import user, event
import os, smtplib, hashlib
from dotenv import load_dotenv
from email.message import EmailMessage

load_dotenv()
# need to install dotenv while shell is open
GMAIL_CODE= os.getenv("gmail_code")

### Hidden Routes

# create
@app.route("/events/new/create", methods=["POST"])
def create_event():
    if "user_id" not in session:
        return redirect("/")
    
    #update new db structure
    #get rid of this and just pass silent id form
    data = {
        "name": request.form["name"],
        "date": request.form["date"],
        "time_start": request.form["time_start"],
        "time_end": request.form["time_end"],
        "address": request.form["address"],
        "details": request.form["details"],
        "options": request.form["options"],
        "guests": request.form["guests"],
        "public" : request.form["public"],
        "user_id": session["user_id"]
    }

    #need validation to block user from adding a connection to his own email into the many-to-many table

    # validate event not currently working

    if not event.Event.validate_event(data):
        return redirect("/events/new/create_one")

    event.Event.create(data)
    return redirect("/dashboard")

# edit/update
@app.route("/events/update/<int:id>", methods=["post"])
def edit_event(id):
    #checks a user is logged in and verifies his or her user_id matches the creator of the event
    if (not (session.get("user_id", False))) or (not (session.get("user_id", False) == event.Event.get_event_by_id({"id" : id}).user_id)):
        session.clear()
        flash("Sorry this event must exist and you must be the owner of it to edit.", "sign_in")
        return redirect("/")
    
    #get rid of this and pass silent id form
    data = {
        "id":id,
        "name": request.form["name"],
        "date": request.form["date"],
        "time_start": request.form["time_start"],
        "time_end": request.form["time_end"],
        "address": request.form["address"],
        "details": request.form["details"],
        "options": request.form["options"],
        "guests": request.form["guests"],
        "public" : request.form["public"],
        "user_id": session["user_id"]
    }

    #need validation to block user from adding a connection to his own email into the many-to-many table

    # validate event not currently working

    if not event.Event.validate_event(data):
        return redirect("/events/edit/"+str(id))

    event.Event.update(data)
    return redirect("/dashboard")

# delete
@app.route("/events/delete/<int:id>")
def delete_event(id):
    #checks a user is logged in and verifies his or her user_id matches the creator of the event
    if (not (session.get("user_id", False))) or (not (session.get("user_id", False) == event.Event.get_event_by_id({"id" : id}).user_id)):
        session.clear()
        flash("Sorry this event must exist and you must be the owner of it to delete.", "sign_in")
        return redirect("/")
    data = {
        "id":id
    }
    event.Event.delete(data)
    return redirect("/dashboard")

@app.route("/events/view/<int:id>/invite", methods=["POST"])
def attend_event(id):
    #checks a user is logged in and verifies his or her user_id matches the creator of the event
    if (not (session.get("user_id", False))) or (not (session.get("user_id", False) == event.Event.get_event_by_id({"id" : id}).user_id)):
        session.clear()
        flash("Sorry this event must exist and you must be the owner of it to edit.", "sign_in")
        return redirect("/")
    
    if not user.User.validate_non_user(request.form):
        return redirect("/events/view/"+str(id))

    event_id={
        "id":id
    }
    this_event=event.Event.get_event_by_id(event_id)

    #separate email message if the email is registered with a user
    invited_user = user.User.get_user_by_email(request.form)
    if invited_user:
        event_link="http://localhost:5000/dashboard"
        user_input={
            "email":request.form["email"]
        }

        # is there a way to add a text body to specify the user can view this and RSVP by logging into the dashboard?
        rsvp_email= "rsvptester16@gmail.com"
        msg = EmailMessage()
        msg.set_content(event_link)
        msg["Subject"] = f'You have been invited to {this_event.name}!'
        msg["From"] = rsvp_email
        msg["To"] = user_input["email"]

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(rsvp_email, GMAIL_CODE)
        server.send_message(msg)

        data = {
            "user_id" : invited_user.id,
            "event_id" : this_event.id,
            "guest_number" : "NULL",
            "attending" : "3"
        }
        user.User.link_users_invitees(data)

        return redirect("/success")

    #email message if invitee email is not registered as a user
    else :
        data = {
            "name" : request.form["name"],
            "email" : request.form["email"],
            "guest_number" : "NULL",
            "attending" : "3",
            "token" : "NULL"
        }
        non_user_id = user.User.non_user_save(data)
        #generate token
        encoded_message = str(non_user_id).encode()
        token = hashlib.sha3_256(encoded_message).hexdigest()
        user.User.update_token({"id" : non_user_id, "token" : token})

        event_link=f"http://localhost:5000/events/view/{event_id['id']}/{token}"

        user_input={
            "email":request.form["email"]
        }

        # is there a way to add a text body to tell the person to not share the personal link and they can update their RSVP by going back there?
        #set_content is body of message
        rsvp_email= "rsvptester16@gmail.com"
        msg = EmailMessage()
        msg.set_content(event_link)
        msg["Subject"] = f'You have been invited to {this_event.name}!'
        msg["From"] = rsvp_email
        msg["To"] = user_input["email"]

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(rsvp_email, GMAIL_CODE)
        server.send_message(msg)
        return redirect("/success")

#not sure what 4 following lines with code are doing - can we delete them?

# send email invite
# app.route("/events/view/<int:id>/attend")
# def invite_one(id):
#     pass

# this is where the view event sub form for a loaded non_user with a token would go
@app.route("/laterlater")
def thingie():
    #data should have keys for "email" and "token"
    user.User.verify_non_user_email(data)

# visible routes


# dashboard/viewall
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/")
    # data = {
    #     "id" : session["user_id"]
    # }
    # user_data=user.User.get_user_by_id(data)
    # print(GMAIL_CODE)
    all_events=event.Event.get_all_events()
    my_events = []
    invited_events = []
    public_events = []
    for single_event in all_events:
        if session["user_id"] == single_event.user_id:
            my_events.append(single_event)
            continue
        for invite in single_event.users_invites:
            if (session["user_id"] == invite[0]) and (invite[3] == "3"):
                invited_events.append(single_event)
                continue
        if single_event.public == 1:
            public_events.append(single_event)
    return render_template("dashboard.html", my_events=my_events, invited_events=invited_events, public_events=public_events)

# create
@app.route("/events/new/create_one")
def create_one():
    if "user_id" not in session:
        return redirect("/")
    return render_template("create_event.html")

# edit/update
@app.route("/events/edit/<int:id>")
def edit_one(id):
    #checks a user is logged in and verifies his or her user_id matches the creator of the event
    if (not (session.get("user_id", False))) or (not (session.get("user_id", False) == event.Event.get_event_by_id({"id" : id}).user_id)):
        session.clear()
        flash("Sorry this event must exist and you must be the owner of it to edit.", "sign_in")
        return redirect("/")
    event_data={
        "id":id
    }
    data=event.Event.get_event_by_id(event_data)
    return render_template("edit_one_event.html", data=data)

#view one event combined route and file and also a token link for anonymous users
#only invited individuals whose emails are not in the user table will be assigned a token
@app.route("/events/view/<int:id>/<token>")
def save_token(id, token):
    session["token"] = [id, token]
    return redirect("/events/view/"+str(id))

@app.route("/events/view/<int:id>")
def view_one(id):
    event_data={
        "id":id
    }
    one_event=event.Event.get_event_by_id(event_data)

    #change ability to view page if event is private
    the_creator = False
    if session.get("user_id", False) == one_event.user_id:
        the_creator = True
    if one_event.public == "0":
        user_access = False
        if the_creator:
            user_access = True
        for invite in one_event.users_invites:
            if session["user_id"] == invite[0]:
                user_access = True
        if not ((user_access) or (session.get("token", [False, False])[0] == event_data.id)):
            session.clear()
            flash("Sorry there must have been a url error; try to only click on or to to provided links. Logged out.", "sign_in")
            return redirect("/")

    logged_in = False
    token = False
    token_entry = ""
    if "user_id" in session:
        logged_in = True
    if "token" in session:
        token = True
        token_entry = user.User.get_non_user_invitee_by_token({"token" : session["token"][1]})

    return render_template("view_one_event.html", one_event=one_event, the_creator=the_creator, logged_in=logged_in, token=token, token_entry=token_entry)

# # view one
# @app.route("/events/view/<int:id>")
# def view_one(id):
#     if "user_id" not in session:
#         return redirect(f"/non_user/events/view/{id}")
#     event_data={
#         "id":id
#     }
#     one_event=event.Event.get_event_by_id(event_data)
#     print(one_event)
#     return render_template("show_one_event_user.html", one_event=one_event)

# @app.route("/non_user/events/view/<int:id>")
# def view_one_non_user(id):
#     if "user_id" in session:
#         return redirect(f"/events/view/{id}")
#     event_data={
#         "id":id
#     }
#     one_event=event.Event.get_event_by_id(event_data)
#     print(one_event)
#     return render_template("show_one_event_non_user.html", one_event=one_event)

@app.route("/success")
def success():
    return render_template("success.html")

