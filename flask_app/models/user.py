from flask_app.config.mysqlconnection import connectToMySQL
from flask_app import app
from flask import flash
from flask_bcrypt import Bcrypt
import re
from flask_app.models import event

bcrypt = Bcrypt(app)
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class User:
    db_name = 'rsvp_schema'

    def __init__(self, data) -> None:
        ## PK
        self.id = data["id"]

        #Cols
        self.first_name = data["first_name"]
        self.last_name = data["last_name"]
        self.email = data["email"]
        self.password = data["password"]
        self.created_at = data["created_at"]
        self.updated_at = data["updated_at"]

        self.events=[]

    # Create new user method
    @classmethod
    def save(cls, data):
        # Successfull DB test
        query = """INSERT INTO users(first_name, last_name, email, password)
                    VALUES(%(first_name)s, %(last_name)s, %(email)s, %(password)s)"""
        result = connectToMySQL(cls.db_name).query_db(query, data)
        return result

    #Get user by email !!Unsafe (password)
    @classmethod
    def get_user_by_email(cls, data):
        # Successfull DB test
        query = """SELECT * FROM users WHERE email=%(email)s"""
        results = connectToMySQL(cls.db_name).query_db(query, data)
        if len(results) == 0:
            return False
        return cls(results[0])

    @classmethod
    def get_non_user_by_email(cls, data):
        query = """SELECT * FROM non_user_invitees WHERE email=%(email)s"""
        results = connectToMySQL(cls.db_name).query_db(query, data)
        if len(results) == 0:
            return False
        return results[0]

    @classmethod
    def link_users_invitees(cls, data):
        query = """INSERT INTO user_invitees (user_id, event_id, attending, guest_number)
                    VALUES (%(user_id)s, %(event_id)s, %(attending)s, %(guest_number)s)"""
        result = connectToMySQL(cls.db_name).query_db(query, data)
        return result

    @classmethod
    def non_user_save(cls, data):
        query = """INSERT INTO non_user_invitees (name, email, attending, guest_number, token, event_id)
                    VALUES (%(name)s, %(email)s, %(attending)s, %(guest_number)s, %(token)s, %(event_id)s)"""
        return connectToMySQL(cls.db_name).query_db(query, data)

    @classmethod
    def non_user_update(cls, data):
        query = """UPDATE non_user_invitees SET name=%(name)s, attending=%(attending)s,
                    guest_number=%(guest_number)s
                    WHERE token=%(token)s"""
        return connectToMySQL(cls.db_name).query_db(query, data)


    @classmethod
    def update_token(cls, data):
        query = "UPDATE non_user_invitees SET token = %(token)s WHERE id = %(id)s;"
        print("Updating ", data["id"])
        return connectToMySQL(cls.db_name).query_db(query, data)

    @classmethod
    def get_non_user_invitee_by_token(cls, data):
        query = """SELECT * FROM non_user_invitees WHERE token=%(token)s"""
        results = connectToMySQL(cls.db_name).query_db(query, data)
        if len(results) == 0:
            return False
        return results[0]
    
    @classmethod
    def get_user_invitee(cls, data):
        query = "SELECT * FROM user_invitees WHERE user_id=%(user_id)s AND event_id=%(event_id)s"
        results = connectToMySQL(cls.db_name).query_db(query, data)
        print(results)
        if len(results) == 0:
            return False
        return results[0]
    
    @classmethod
    def user_invitee_update(cls, data):
        query = """UPDATE user_invitees SET attending=%(attending)s,
                    guest_number=%(guest_number)s
                    WHERE user_id=%(user_id)s AND event_id=%(event_id)s"""
        return connectToMySQL(cls.db_name).query_db(query, data)

    @classmethod
    def swip_swap_kapop(cls, data):
        query = """DELETE FROM non_user_invitees WHERE token=%(token)s"""
        connectToMySQL(cls.db_name).query_db(query, data)
        query = """INSERT INTO users (first_name, last_name, email, password)
            VALUES(%(first_name)s, %(last_name)s, %(email)s, %(password)s)"""
        user_id = connectToMySQL(cls.db_name).query_db(query, data)

        data2 = {
            "user_id" : user_id,
            "event_id" : data["event_id"],
            "attending" : 3,
            "guest_number" : "NULL"
        }
        query = """INSERT INTO user_invitees (user_id, event_id, attending, guest_number)
                    VALUES (%(user_id)s, %(event_id)s, %(attending)s, %(guest_number)s)"""
        connectToMySQL(cls.db_name).query_db(query, data2)
        return user_id

    #Untested method
    @staticmethod
    def validate_user(user):
        #should take user dictionary from registration form with keys for "first_name", "last_name", "email", and "password"
        #verifies all fields are present and valid
        #checks email is not already in use
        #checks password and "confirm_password" are the same
        #returns T or F boolean
        return True

        is_valid = True
        pw_invalid = False
        if len(user['first_name']) < 2 or len(user['last_name']) < 2:
            flash("* Field Required: Name", 'Register')
            is_valid = False
        if not EMAIL_REGEX.match(user['email']):
            flash("* Invalid Email Format", 'Register')
            is_valid = False            
        if len(user['email']) < 1: 
            flash("* Field Required: Email", 'Register')
            is_valid = False
        if not user['password']:
            flash("* Field Required: Password", 'Register')
        if user['password'] != user['confirm_password']:
            flash("* Passwords do not match!", "Register")
            is_valid = False

        #this should just be a simple method check to see if a record is returned with the specific email, no need for a "for loop"
        all_users = User.get_all_users()
        if all_users:
            for db_user in all_users:
                if user['email'] == db_user.email:
                    flash("* Email has been taken", "Register")
                    is_valid = False
        
        # creates a list of each character in the password like ['a', 'b', 'c']
        pw = [letter for letter in user['password']]
        
        ## If any of these statement return false -> set password invalid true

        # any() checks for any True --- ### --- any([False, False, True, False]) -> True
        # checks if any character in the pw is a digit -> if so return True and move on
        if not any(char.isdigit() for char in pw):
            pw_invalid = True
        # same but for upper case -> if no char is lower return false and pw_invalid = True
        if not any(char.isupper() for char in pw):
            pw_invalid = True
        # same but for lower case
        if not any(char.islower() for char in pw):
            pw_invalid = True
        # finally check length
        if len(user['password']) < 6:
            pw_invalid = True

        ## If the password is invalid, the 
        if pw_invalid:
            flash("""* Password must contain one of each of the following
                    \n- An uppercase letter
                    \n- A lowercase letter
                    \n- A number
                    \n- Must be longer than 6 characters""", "Register")
            is_valid = False

        return is_valid

    @staticmethod
    def validate_non_user(data):
        #data is a dictionary from a form to send event invites- must make sure keys are present and valid for "name" and "email" only
        #the email address must not be associated with the user record who is the creator for the event
        #email address cannot be present in the records for this event that show up in the user_invitee table
        # returns T or F boolean
        return True

# flash("Sorry, this user has already been invited to your event.  Ask them to check their emails, including the junk box.", "invite")

    @staticmethod
    def verify_non_user_email(data):
        #data is a dictionary from a form.  verify that the keys for "email" and "token" are both a part of the same exact entry in non_user_invitees table
        #flash that email and token need to be same record
        print(data)
        
        return True







    @classmethod
    def get_one_user_with_events(cls, data):
        query = "SELECT * FROM users LEFT JOIN events ON users.id = events.user_id WHERE users.id = %(user_id)s"
        results = connectToMySQL(cls.db_name).query_db(query, data)
        if len(results) == 0:
            return None
        else:
            user_instance = cls(results[0])
            for this_event_dictionary in results:
                if this_event_dictionary['events.id'] == None:
                    break
                new_event_dictionary = {
                    "id": this_event_dictionary['events.id'],
                    "user_id":this_event_dictionary['user_id'],
                    "name": this_event_dictionary['name'],
                    "date": this_event_dictionary['date'],
                    "time_start": this_event_dictionary['time_start'],
                    "time_end": this_event_dictionary['time_end'],
                    "address": this_event_dictionary['address'],
                    "details": this_event_dictionary['details'],
                    "options": this_event_dictionary['options'],
                    "plus_one": this_event_dictionary['plus_one'],
                    "created_at": this_event_dictionary['events.created_at'],
                    "updated_at": this_event_dictionary['events.updated_at']
                }
                this_event_object = event.Event(new_event_dictionary)
                user_instance.events.append(this_event_object)
            return user_instance

    # Get all users !!Unsafe (password)
    @classmethod
    def get_all_users(cls):
        # Successfull DB test
        query = """SELECT * FROM users"""

        result = connectToMySQL(cls.db_name).query_db(query)

        return result

    #returns user by id !!Unsafe (password)
    @classmethod
    def get_user_by_id(cls, data):
        # Successfull DB test
        query = """SELECT * FROM users WHERE id=%(id)s"""

        results = connectToMySQL(cls.db_name).query_db(query, data)

        if len(results) == 0:
            return False

        return cls(results[0])

    @classmethod
    def check_if_email_in_system(cls, data):
        query = "SELECT * FROM users WHERE email = %(email)s"
        results = connectToMySQL(cls.db_name).query_db(query, data)
        # if the query returns nothing, it is false.
        if not results:
            return False
        else:
            return True

    @classmethod
    def update_user(cls, data):
        # Successfull DB test
        query = """UPDATE users SET first_name=%(first_name)s, last_name=%(last_name)s,
                    email=%(email)s, password=%(password)s
                    WHERE id=%(id)s"""

        results = connectToMySQL(cls.db_name).query_db(query, data)

    @classmethod
    def delete(cls, data):
        # Untested in DB
        query = "DELETE FROM users WHERE id=%(id)s"

        result = connectToMySQL(cls.db_name).query_db(query, data)