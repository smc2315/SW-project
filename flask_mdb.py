from flask import *
from flask_pymongo import PyMongo

web_bulletin = Flask(__name__, template_folder="templates")
web_bulletin.config["MONGO_URI"] = "mongodb://localhost:27017/bulletin"
web_bulletin.config['SECRET_KEY'] = 'psswrd'

mongo = PyMongo(web_bulletin)

web_bulletin.secret_key = 'psswrd'


@web_bulletin.route("/signup", methods=["GET", "POST"])
def bulletin_write():
    if request.method == "POST":
        email = request.form.get("email", type=str)
        pw = request.form.get("password", type=str)
        pw2 = request.form.get("passwordagain", type=str)
        username = request.form.get("username", type=str)
        name = request.form.get("name", type=str)
        if email == "":
            flash("Please Input Email")
            return render_template("signup.html")
        elif pw == "":
            flash("Please Input Password")
            return render_template("signup.html")
        elif pw2 == "":
            flash("Please Input Password-again")
            return render_template("signup.html")
        elif username == "":
            flash("Please Input UserName")
            return render_template("signup.html")
        elif name == "":
            flash("Please Input Name")
            return render_template("signup.html")
        elif pw != pw2:
            flash("Password is not correct!")
            return render_template("signup.html")
        signup = mongo.db.signup
        check_cnt = signup.count_documents({"email": email})
        if check_cnt > 0:
            flash("it is a registered email")
            return render_template("signup.html")
        to_db = {
            "email": email,
            "pw": pw,
            "username": username,
            "name": name,
        }
        to_db_signup = signup.insert_one(to_db)
        last_signup = signup.find().sort("_id", -1).limit(5)
        for _ in last_signup:
            print(_)

        flash("Thanks fot your signup")
        return render_template("signup.html")
    else:
        return render_template("signup.html")


if __name__ == "__main__":
    web_bulletin.run(host='127.0.0.1', debug=True, port=9999)
