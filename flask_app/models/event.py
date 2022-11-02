from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_app.models import user
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')


class Event():
    db_name = 'rsvp_schema'
    def __init__(self, data) -> None:
        ## PK
        self.id = data["id"]

        #Cols
        self.name = data["name"]
        self.date = data["date"]
        self.time_start = data["time_start"]
        self.time_end = data["time_end"]
        self.address = data["address"]
        self.details = data["details"]
        self.options = data["options"]
        self.guests = data["guests"]
        self.geodata = "" # leave blank for now unless Cody may need this
        self.public = data["public"] #!!!!!!! 0 is no public or private; 1 is public event
        self.created_at = data["created_at"]
        self.updated_at = data["updated_at"]
        
        ## FK
        self.user_id = data["user_id"]
        # keep track of who made the event
        self.creator = None

        #user_invites stores many to many relationship in list format for user_invitees table [user_id, event_id, guest_number, attending]
        self.users_invites = []

    @classmethod
    def create(cls, data):
        # Successfull test in DB
        query = """INSERT INTO events(name, date, time_start, time_end, address,
                    details, options, guests, geodata, public, user_id)
                    VALUES(%(name)s, %(date)s, %(time_start)s, %(time_end)s, %(address)s,
                    %(details)s, %(options)s, %(guests)s, "NULL", %(public)s, %(user_id)s)"""
        result = connectToMySQL(cls.db_name).query_db(query, data)
        return result

    @classmethod
    def get_all_events(cls):
        query = """SELECT * FROM events"""
        result = connectToMySQL(cls.db_name).query_db(query)
        event_list = []
        for row in result:
            event_obj = cls(row)
            data = {"id" : event_obj.id}
            query ="""SELECT * FROM user_invitees WHERE event_id=%(id)s"""
            result = connectToMySQL(cls.db_name).query_db(query, data)
            for invite in result:
                record_list = [invite["user_id"], invite["event_id"], invite["guest_number"], invite["attending"]]
                event_obj.users_invites.append(record_list)
            event_list.append(event_obj)
        return event_list

    @classmethod
    def get_event_by_id(cls, data):
        query ="""SELECT * FROM events WHERE id=%(id)s"""
        result = connectToMySQL(cls.db_name).query_db(query, data)
        if len(result) == 0:
            return False
        event_obj = cls(result[0])
        invitee_data = {"id" : event_obj.id}
        query ="""SELECT * FROM user_invitees WHERE event_id=%(id)s"""
        result2 = connectToMySQL(cls.db_name).query_db(query, invitee_data)
        for invite in result2:
            record_list = [invite["user_id"], invite["event_id"], invite["guest_number"], invite["attending"]]
            event_obj.users_invites.append(record_list)
        return event_obj

    # @classmethod
    # def time_test_id(cls, data):
    #     query = """SELECT TIME_FORMAT(time_start, '%%r') FROM events where id=%(id)s"""
    #     result = connectToMySQL(cls.db_name).query_db(query, data)
    #     print(result)


    @classmethod
    def update(cls, data):
        # Untested in DB
        query = "UPDATE events SET name=%(name)s, date=%(date)s, time_start=%(time_start)s, time_end=%(time_end)s, address=%(address)s, details=%(details)s, options=%(options)s, guests=%(guests)s, public=%(public)s, user_id=%(user_id)s WHERE id=%(id)s"
        result = connectToMySQL(cls.db_name).query_db(query, data)
        return result

    @classmethod
    def delete(cls, data):
        query = """DELETE FROM events WHERE id=%(id)s"""
        result = connectToMySQL(cls.db_name).query_db(query, data)
        return result

    @staticmethod
    def verify_nUnT_invite(data):
        is_valid=True
        if len(data['name'].strip()) < 2:
            is_valid=False
            flash("Name must be at least 2 characters.")
        if len(data['email'].strip()) < 5:
            is_valid=False
            flash("Email must be at least 5 characters.")
        if not EMAIL_REGEX.match(data["email"].strip()):
            flash('Invalid Email')
            is_valid = False
        if len(data['guest_number'].strip()) < 1:
            is_valid=False
            flash("Must specify number of guests you are bringing including yourself.")
        if len(data['attending'].strip()) < 1:
            is_valid=False
            flash("Please select if you are attending or not.")
        if user.User.get_non_user_by_email(data):
            is_valid=False
            flash("You have already been invited to this event, please check your email for the invite.")
        if user.User.get_user_by_email(data):
            is_valid=False
            flash("Please sign into your account to RSVP to the event.")
        return is_valid

    @staticmethod
    def verify_T_invite(data):
        #gets dictionary with name, email, guest_number, and attending keys
        #check guest_number is not larger than allowed
        is_valid=True
        if len(data['name'].strip()) < 2:
            is_valid=False
            flash("Name must be at least 2 characters.")
        if len(data['email'].strip()) < 5:
            is_valid=False
            flash("Email must be at least 5 characters.")
        if not EMAIL_REGEX.match(data["email"].strip()):
            flash('Invalid Email', 'register')
            is_valid = False
        if len(data['guest_number'].strip()) < 1:
            is_valid=False
            flash("Must specify number of guests you are bringing including yourself.")
        if len(data['attending'].strip()) < 1:
            is_valid=False
            flash("Please select if you are attending or not.")
        return is_valid


    @staticmethod
    def validate_event(data):
        def contains_number(string):
            return any(char.isdigit() for char in string)
        isValid = True
        if len(data['name']) < 2:
            flash("Event name must be at least 2 characters.")
            isValid = False
        if len(data['date']) < 2:
            flash("Please input a date")
            isValid = False
        if len(data['time_start']) < 2:
            flash("Please input a start time")
            isValid = False
        if len(data['time_end']) < 2:
            flash("Please input a end time")
            isValid = False
        if len(data['address']) < 5:
            flash("Address must be at least 5 characters.")
            isValid = False
        if not contains_number(data['address']):
            flash("Address must have numbers.")
        if len(data['details']) < 2:
            flash("Details must be at least 2 characters.")
            isValid = False
        if len(data['guests']) < 1:
            flash("Please input a number of allowed guests.")
            isValid = False
        if len(data['public']) < 1:
            flash("Please choose if the event is public or private.")
            isValid = False
        return isValid
