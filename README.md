# Dojo-Group-Project
 Coding Dojo Group Project Group #16

Groupies -> 
1. Clone repository and run "python -m pipenv install -r requirements.txt" inside of directory
2. Currently installed flask and pymysql
3. If we need to add more packages, let the group know and update the requirements.txt
4. to update the requirements text on your computer:
    1. delete current requirements.txt
    2. cd into project directory
    3. "python -m pipenv shell"
    4. "pip freeze > requirements.txt"





## PROJECT NAME
1. Users 
    - Login : Email, Password
    - Register: First name, Last name, email, password
2. Events
    - Create:
        1. Event name
        2. Date
        3. Details
        4. Location
        5. Options (like food)
        6. +1
        7. Additional Details
    - Read: 
        1. Read all above data
        2. Link to event from email directs to this page, OR, from website dashboard details page
    - Update:
        1. Update all data in event
        2. Form is pre filled with current data
    - Delete: 
        1. Delete event, remove to dashboard
        2. Delete from db after event date?
        3. Old links redirect to a 404 page
3. Email Option:
    - Send "card" through email with event details and link
    - Link brings you to event read page
    - Yes/No
4. Comments:
    - Users can comment on events
    - basic CRUD on Comments
5. Front-End Frameworks:
    - Bootstrap or Tailwind
    - Custom CSS
