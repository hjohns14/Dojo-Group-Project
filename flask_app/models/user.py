from flask_app.config.mysqlconnection import connectToMySQL
from flask_app import app
from flask import flash
from flask_bcrypt import Bcrypt
import re

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


    # Create new user method
    @classmethod
    def save(cls, data):

        # Successfull DB test
        query = """INSERT INTO users(first_name, last_name, email, password)
                    VALUES(%(first_name)s, %(last_name)s, %(email)s, %(password)s)"""
        
        result = connectToMySQL(cls.db_name).query_db(query, data)

        return result

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
    def check_if_email_in_system(cls, data):
        query = "SELECT * FROM users WHERE email = %(email)s"
        results = connectToMySQL(cls.db).query_db(query, data)
        # if the query returns nothing, it is false.
        if not results:
            return False
        else:
            return True

    #### If we need safe methods to get a user without password info write them here
    #
    #
    #

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


    #Untested method
    @staticmethod
    def validate_registration(user):
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