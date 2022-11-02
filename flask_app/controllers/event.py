from flask import render_template, request, redirect, session, flash, request
from flask_app import app
from flask_app.models import user, event, maps
import os, smtplib, hashlib
from dotenv import load_dotenv
from email.message import EmailMessage
import re
from datetime import datetime
import time

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

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
    print(data["time_end"])

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
def attend_event_email(id):
    #checks a user is logged in and verifies his or her user_id matches the creator of the event
    #must add a verify validation to ensure that the submitted email is correct and works with smtplib
    if (not (session.get("user_id", False))) or (not (session.get("user_id", False) == event.Event.get_event_by_id({"id" : id}).user_id)):
        session.clear()
        flash("Sorry this event must exist and you must be the owner of it to edit.", "sign_in")
        return redirect("/")

    event_id={
        "id":id
    }
    this_event=event.Event.get_event_by_id(event_id)

    if len(request.form['name'])<2 or len(request.form['email'])<5:
        flash("Must have a name and email to invite someone")
        return redirect(request.referrer)

    if not EMAIL_REGEX.match(request.form["email"].strip()):
        flash("Invalid Email")
        return redirect(request.referrer)

    
    #separate email message if the email is registered with a user
    invited_user = user.User.get_user_by_email(request.form)
    if invited_user:
        event_link="http://localhost:5000/dashboard"

        data = {
            "user_id" : invited_user.id,
            "event_id" : this_event.id,
            "guest_number" : "0",
            "attending" : "3"
        }

        rsvp_email= "rsvptester16@gmail.com"
        msg = EmailMessage()
        msg.set_content(event_link)
        msg["Subject"] = f'You have been invited to {this_event.name}!'
        msg["From"] = rsvp_email
        msg["To"] = request.form["email"]

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(rsvp_email, GMAIL_CODE)
        server.send_message(msg)


        user.User.link_users_invitees(data)

        return redirect("/success")

    #email message if invitee email is not registered as a user
    else :
        data = {
            "name" : request.form["name"],
            "email" : request.form["email"],
            "attending" : "3",
            "guest_number" : "0",
            "token" : "NULL",
            "event_id" : id
        }
        all_invited=user.User.get_all_non_users()
        check_if_email_invited_to_event = [k for k in all_invited if k['email'] == data["email"]]
        if check_if_email_invited_to_event:
            check_if_invited_this_event=[k for k in check_if_email_invited_to_event if k['event_id'] == data["event_id"]]
            if check_if_invited_this_event:
                print(check_if_invited_this_event)
                flash("Sorry, this user has already been invited to your event. Ask them to check their emails, including the junk box.")
                return redirect("/events/view/"+str(id))

        non_user_id = user.User.non_user_save(data)
        #generate token
        encoded_message = str(non_user_id).encode()
        token = hashlib.sha3_256(encoded_message).hexdigest()
        user.User.update_token({"id" : non_user_id, "token" : token})

        event_link=f"http://localhost:5000/events/view/{event_id['id']}/{token}"

        rsvp_email= "rsvptester16@gmail.com"
        msg = EmailMessage()
        msg.set_content(event_link)
        msg["Subject"] = f'You have been invited to {this_event.name}!'
        msg["From"] = rsvp_email
        msg["To"] = request.form["email"]

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(rsvp_email, GMAIL_CODE)
        server.send_message(msg)
        return redirect("/success")

@app.route("/events/view/<int:id>/nUnT/attend", methods=["POST"])
def attend_event_nUnT(id):
    #verify event is public
    one_event=event.Event.get_event_by_id({"id" : id})
    if one_event.public == 0:
        session.clear()
        flash("Sorry there must have been a url error; try to only click on or to to provided links. Logged out.", "sign_in")
        return redirect("/")

    data = {
    "name" : request.form["name"],
    "email" : request.form["email"],
    "attending" : request.form["attending"],
    "guest_number" : request.form["guest_number"],
    "token" : "NULL",
    "event_id" : id
    }

    if not event.Event.verify_nUnT_invite(data):
        return redirect(request.referrer)

    if len(data["attending"]) < 1:
        flash("Must select whether you are attending or not to RSVP.")
        return redirect(request.referrer)


    if data["guest_number"] == "":
        data["guest_number"] = 0

    if int(data["guest_number"]) > int(one_event.guests):
        flash("Your number of guests must be less than the maximum number of guests allowed.")
        return redirect(request.referrer)

    user.User.non_user_save(data)
    return redirect("/success/2")

# @app.route("/events/view/<int:id>/token/register", methods=["POST"])
# def token_user_register(id):
#     #data should have keys for "email" and "token"
#     #add protections to verify not logged in and there is a token in session
#     data = {
#     "first_name" : request.form["first_name"],
#     "last_name" : request.form["last_name"],
#     "email" : request.form["email"],
#     "password" : request.form["password"],
#     "confirm_password" : request.form["confirm_password"],
#     "token" : session["token"][1],
#     "event_id" : id
#     }
#     if not user.User.validate_user(data):
#         return redirect(request.referrer)
#     if not user.User.verify_non_user_email(data):
#         return redirect(request.referrer)

#     user_id = user.User.swip_swap_kapop(data)
#     session["user_id"] = user_id
#     return redirect("/")

@app.route("/events/view/<int:id>/token/attend", methods=["POST"])
def token_attend(id):
    data = {
    "name" : request.form["name"],
    "email" : request.form["email"],
    "attending" : request.form["attending"],
    "guest_number" : request.form["guest_number"],
    "token" : session["token"][1],
    "event_id" : id
    }

    one_event=event.Event.get_event_by_id({"id" : id})


    if not event.Event.verify_T_invite(data):
        return redirect(request.referrer)

    if len(data["attending"]) < 1:
        flash("Must select whether you are attending or not to RSVP.")
        return redirect(request.referrer)

    
    if data["guest_number"] == "":
        data["guest_number"] = 0

    if int(data["guest_number"]) > int(one_event.guests):
        flash("Your number of guests must be less than the maximum number of guests allowed.")
        return redirect(request.referrer)

    user.User.non_user_update(data)
    return redirect("/success/3")

@app.route("/events/view/<int:id>/logged-in/attend", methods=["POST"])
def logged_in_attend(id):
    one_event=event.Event.get_event_by_id({"id" : id})

    data = {
    "user_id" : session["user_id"],
    "event_id" : id,
    "attending" : request.form["attending"],
    "guest_number" : request.form["guest_number"],
    }

    if data["guest_number"] == "":
        data["guest_number"] = 0

    if int(data["guest_number"]) > int(one_event.guests):
        print(one_event.guests,"guest")
        print(data["guest_number"])
        flash("Your number of guests must be less than the maximum number of guests allowed.")
        return redirect(request.referrer)

    if len(data["attending"]) < 1:
        flash("Must select whether you are attending or not to RSVP.")
        return redirect(request.referrer)

    temp = user.User.get_user_invitee({"user_id" : session["user_id"], "event_id" : id})
    if temp:
        user.User.user_invitee_update(data)
    else :
        user.User.link_users_invitees(data)
    
    return redirect("/success/3")


# this is where the view event sub form for a loaded non_user with a token would go

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
    my_attending_events = []
    invited_events = []
    public_events = []
    for single_event in all_events:
        if session["user_id"] == single_event.user_id:
            my_events.append(single_event)
            continue
        for invite in single_event.users_invites:
            if (session["user_id"] == invite[0]) and (invite[3] == 1):
                my_attending_events.append(single_event)
                continue
        for invite in single_event.users_invites:
            if (session["user_id"] == invite[0]) and (invite[3] == 3):
                invited_events.append(single_event)
                continue
        if single_event.public == 1:
            public_events.append(single_event)
    return render_template("dashboard.html", my_attending_events=my_attending_events, my_events=my_events, invited_events=invited_events, public_events=public_events)

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
    if one_event.public == 0:
        user_access = False
        if the_creator:
            user_access = True
        for invite in one_event.users_invites:
            if session["user_id"] == invite[0]:
                user_access = True
        if not ((user_access) or (session.get("token", [False, False])[0] == one_event.id)):
            session.clear()
            return redirect("/")

    logged_in = False
    token = False
    token_entry = ""
    logged_in_entry = ""
    if "user_id" in session:
        logged_in = True
        temp = user.User.get_user_invitee({"user_id" : session["user_id"], "event_id" : id})
        if temp:
            logged_in_entry = temp
        else :
            logged_in_entry = {
                "attending" : 0,
                "guest_number" : 0
            }
    if "token" in session:
        token = True
        token_entry = user.User.get_non_user_invitee_by_token({"token" : session["token"][1]})

    formatted_date = one_event.date.strftime('%m/%d/%Y')
    location = maps.getmapembed(one_event.address)
    str_start_time=str(one_event.time_start)[0:5]
    str_end_time=str(one_event.time_end)[0:5]
    
    return render_template("view_one_event.html", str_end_time=str_end_time, str_start_time=str_start_time, formatted_date=formatted_date, one_event=one_event, the_creator=the_creator, logged_in=logged_in, logged_in_entry=logged_in_entry, token=token, token_entry=token_entry, location=location)

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

@app.route("/success/2")
def success_2():
    return render_template("success_2.html")

@app.route("/success/3")
def success_3():
    return render_template("success_3.html")