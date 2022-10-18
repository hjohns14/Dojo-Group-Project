from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models import user

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
        self.plus_one = data["plus_one"]
        self.created_at = data["created_at"]
        self.updated_at = data["updated_at"]
        
        ## FK
        self.user_id = data["user_id"]
        # keep track of who made the event
        self.creator = None

    @classmethod
    def create(cls, data):
        # Successfull test in DB
        query = """INSERT INTO events(name, date, time_start, time_end, address,
                    details, options, plus_one, user_id)
                    VALUES(%(name)s, %(date)s, %(time_start)s, %(time_end)s, %(address)s,
                    %(details)s, %(options)s, %(plus_one)s, %(user_id)s)"""

        result = connectToMySQL(cls.db_name).query_db(query, data)

        return result

    @classmethod
    def get_all_events(cls):
        query = """SELECT * FROM events"""

        result = connectToMySQL(cls.db_name).query_db(query)

        return result

    @classmethod
    def get_event_by_id_for_one_user(cls, data):
        query ="""SELECT * FROM events JOIN users on users.id = events.user_id WHERE events.id=%(id)s"""

        result = connectToMySQL(cls.db_name).query_db(query, data)

        if len(result) == 0:
            return False
        else:
            print(result,"result")
            event = cls(result[0])
            user_data = {
                "id":result[0]['users.id'],
                "first_name":result[0]['first_name'],
                "last_name":result[0]['last_name'],
                "email":result[0]['email'],
                "password":result[0]['password'],
                "created_at":result[0]['users.created_at'],
                "updated_at":result[0]['users.updated_at']
            }
            event_maker = user.User(user_data)
            event.creator = event_maker
            print(event)
            return event

    @classmethod
    def get_event_by_id(cls, data):
        query ="""SELECT * FROM events WHERE id=%(id)s"""

        result = connectToMySQL(cls.db_name).query_db(query, data)

        if len(result) == 0:
            return False
        return result

    @classmethod
    def update(cls, data):
        # Untested in DB
        query = "UPDATE events SET name=%(name)s, date=%(date)s, time_start=%(time_start)s, time_end=%(time_end)s, address=%(address)s, details=%(details)s, options=%(options)s, plus_one=%(plus_one)s, user_id=%(user_id)s WHERE id=%(id)s"

        result = connectToMySQL(cls.db_name).query_db(query, data)
        return result

    
    @classmethod
    def delete(cls, data):
        query = """DELETE FROM events WHERE id=%(id)s"""

        connectToMySQL(cls.db_name).query_db(query, data)


    @staticmethod
    def validate_event(data):
        isValid = True

        # Validations (we can decide what we want to validate later on and add here)
        if len(data['name'] < 2):
            isValid = False

        return isValid

    