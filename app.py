import gridfs
from flask import Flask, render_template, redirect, request, url_for, session, flash, escape
from flask_pymongo import PyMongo
from datetime import datetime, timedelta

app = Flask(__name__, template_folder="templates")
app.config["MONGO_URI"] = "mongodb://localhost:27017/bulletin"
app.config['SECRET_KEY'] = 'psswrd'

mongo = PyMongo(app)

app.secret_key = 'psswrd'


@app.route('/')
def main():
    userid = session.get('userid', None)
    logFlag = session.get('logFlag', None)
    results = mongo.db.post.find()

    return render_template("main.html", userid=userid, logFlag=logFlag, data=results)


@app.route("/signup", methods=["GET", "POST"])
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

        flash("Thanks for your signup")
        return render_template("main.html")
    else:
        return render_template("signup.html")


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        user_id = request.form.get("user_id", type=str)
        user_pw = request.form.get("user_pw", type=str)
        sign_in = mongo.db.signup
        data = sign_in.find_one({"username": user_id})
        if data is None:
            flash("ID does not exist!!")
            return redirect("/signin")
        else:
            if data.get("pw") == user_pw:
                session['userid'] = user_id
                session['logFlag'] = 1

                userid = session.get('userid', None)
                logFlag = session.get('logFlag', None)
                return render_template("main.html", userid=userid, logFlag=logFlag)
            else:
                flash("Wrong Password!!")
                return redirect("/signin")
    else:
        return render_template("signin.html")


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('userid', None)
    return redirect('/')


@app.route('/new', methods=['GET', 'POST'])
def new():
    userid = session.get('userid', None)
    logFlag = session.get('logFlag', None)
    if logFlag != 1:
        flash("Please Login to write post.")
        return render_template("main.html", userid=userid, logFlag=logFlag)
    if request.method == "POST":
        userid = '%s' % escape(session["userid"])
        title = request.form.get("title", type=str)
        body = request.form.get("body", type=str)
        f = request.files['file']
        if title == "":
            flash("title is empty!")
            return render_template("new.html", userid=userid, logFlag=logFlag)
        elif body == "":
            flash("body is empty!")
            return render_template("new.html", userid=userid, logFlag=logFlag)
        elif not f:
            flash("Please upload Picture!")
            return render_template("new.html", userid=userid, logFlag=logFlag)
        else:
            post = mongo.db.post
            for i in f:
                img_id_save = []
                fs = gridfs.GridFS(mongo.db)
                file_img_id = fs.put(i)
                img_id_save.append(file_img_id)
            to_db = {
                "title": title,
                "body": body,
                "flies": list(img_id_save),  # 이미지 업로드 부분 잘 모르겠음.
                "userid": userid,
            }
            post.insert_one(to_db)
            return render_template("main.html", userid=userid, logFlag=logFlag)
    else:
        return render_template("new.html", userid=userid, logFlag=logFlag)


if __name__ == "__main__":
    app.run(host='127.0.0.1', debug=True, port=9999)
