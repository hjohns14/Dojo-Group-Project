from flask import render_template
from flask_app import app

#Import All YOUR CONTROLLERS


#Move routes to controllers files
@app.route('/')
def main():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)