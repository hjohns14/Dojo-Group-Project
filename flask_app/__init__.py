from flask import Flask

app = Flask(__name__)
app.secret_key = "42" ## Change to env when using