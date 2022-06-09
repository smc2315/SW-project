import codecs
import io

import gridfs
from flask import Flask, render_template, redirect, request, url_for, session, flash, escape
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

from datetime import datetime, timedelta

app = Flask(__name__, template_folder="templates")
app.config["MONGO_URI"] = "mongodb://localhost:27017/bulletin"
app.config['SECRET_KEY'] = 'psswrd'

mongo = PyMongo(app)

app.secret_key = 'psswrd'


@app.route('/', methods=["GET", "POST"])
def main():
    userid = session.get('userid', None)
    logFlag = session.get('logFlag', None)

    if request.method == "POST":
        keyword = request.form.get("search_key", type=str)
        results = mongo.db.post.find({"keyword": keyword})
        img = []
        for i in results:
            fs = gridfs.GridFS(mongo.db)
            img_binary = fs.get(i['flies'])
            base64_img = codecs.encode(img_binary.read(), 'base64')
            decoded_img = base64_img.decode('utf-8')
            img.append(decoded_img)
        results = mongo.db.post.find({"keyword": keyword})
        return render_template("main.html", userid=userid, logFlag=logFlag, data=results, img=img)
    else:
        results = mongo.db.post.find()
        img=[]
        for i in results:

            fs = gridfs.GridFS(mongo.db)
            img_binary = fs.get(i['flies'])
            base64_img = codecs.encode(img_binary.read(), 'base64')
            decoded_img = base64_img.decode('utf-8')
            img.append(decoded_img)
        results = mongo.db.post.find()
        return render_template("main.html", userid=userid, logFlag=logFlag, data=results,img=img)


@app.route("/signup", methods=["GET", "POST"])
def signup():
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
            "following": [],
            "follower": [],
        }
        to_db_signup = signup.insert_one(to_db)
        last_signup = signup.find().sort("_id", -1).limit(5)
        for _ in last_signup:
            print(_)

        flash("Thanks for your signup")
        return redirect('/')
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
                return redirect("/")
            else:
                flash("Wrong Password!!")
                return redirect("/signin")
    else:
        return render_template("signin.html")


@app.route('/new', methods=['GET', 'POST'])
def new():
    userid = session.get('userid', None)
    logFlag = session.get('logFlag', None)
    if logFlag != 1:
        flash("Please Login to write post.")
        return redirect("/")
    if request.method == "POST":
        userid = '%s' % escape(session["userid"])
        title = request.form.get("title", type=str)
        body = request.form.get("body", type=str)
        keyword = request.form.get("keyword", type=str)
        price = request.form.get("price", type=str)
        f = request.files['file']
        f2 = request.files['file2']
        if title == "":
            flash("title is empty!")
            return render_template("new.html", userid=userid, logFlag=logFlag)
        elif body == "":
            flash("body is empty!")
            return render_template("new.html", userid=userid, logFlag=logFlag)
        elif keyword == "":
            flash("keyword is empty!")
        elif price == "":
            flash("Please input Price!!")
        elif not f:
            flash("Please upload Picture!")
            return render_template("new.html", userid=userid, logFlag=logFlag)
        elif not f2:
            flash("Please upload Picture2!")
            return render_template("new.html", userid=userid, logFlag=logFlag)
        else:
            post = mongo.db.post

            fs = gridfs.GridFS(mongo.db)
            # for i in f:
            #     img_id_save = []
            file_img_id = fs.put(f)
            file_img_id2 = fs.put(f2)
            # img_id_save.append(file_img_id)
            to_db = {
                "title": title,
                "body": body,
                "flies": file_img_id,
                "flies2": file_img_id2,
                "keyword": keyword,
                "userid": userid,
                "sold": "visibility:hidden",
                "price": price,
            }
            post.insert_one(to_db)
            return redirect("/")
    else:
        return render_template("new.html", userid=userid, logFlag=logFlag)



@app.route('/follow/<username>',methods=['GET', 'POST'])
def follow(username):
    id=username

    mongo.db.signup.update_one({"username":id},{"$push":{"follower":session.get('userid',None)}})
    mongo.db.signup.update_one({"username":session.get('userid',None)},{"$push":{"following":id}})
    result =  mongo.db.signup.find_one({"username":"id"})
    return redirect(url_for('userinfo',username=id))


@app.route('/unfollow/<username>',methods=['GET', 'POST'])
def unfollow(username):
    id=username
    mongo.db.signup.update_one({"username":id},{"$pull":{"follower":session.get('userid',None)}})
    mongo.db.signup.update_one({"username":session.get('userid',None)},{"$pull":{"following":id}})
    result =  mongo.db.signup.find_one({"username":"id"})
    return redirect(url_for('userinfo',username=id))


@app.route('/userinfo', methods=['GET'])
def userinfo():

    id=request.args.get('username')
    userid = session.get('userid',None)
    result = mongo.db.signup.find_one({"username": id})
    data = mongo.db.post.find({"userid": id})
    img = []
    for i in data:
        fs = gridfs.GridFS(mongo.db)
        img_binary = fs.get(i['flies'])
        base64_img = codecs.encode(img_binary.read(), 'base64')
        decoded_img = base64_img.decode('utf-8')
        img.append(decoded_img)
    data = mongo.db.post.find({"userid": id})
    if userid is None:
        followFlag = 2
    else:


        followFlag=0
        u=mongo.db.signup.find_one({"username":userid})
        for _ in u['following']:
            if _ == id:
                followFlag=1
                break
        if id ==userid:
            followFlag=2
    return render_template("mypage.html",result=result,followFlag=followFlag,data=data,img = img,userid=userid)



@app.route('/logout')
def logout():
    session['LogFlag'] = 0
    session.clear()
    return redirect(url_for('main'))


@app.route('/detail/<post_id>', methods=['POST', 'GET'])
def detail(post_id):
    userid = session.get('userid', None)
    post = mongo.db.post
    results = post.find_one({"_id": ObjectId(post_id)})
    setting = ""
    if (results["userid"] != userid) or (results["sold"] == "sold"):
        setting = "visibility:hidden"

    fs = gridfs.GridFS(mongo.db)
    contents = ObjectId(results['flies'])
    contents2 = ObjectId(results['flies2'])
    ff = mongo.db.fs.files.find_one({"_id": ObjectId(contents)})
    ff2 = mongo.db.fs.files.find_one({"_id": ObjectId(contents2)})
    fc = mongo.db.fs.chunks.find_one({"files_id": ff['_id']})
    fc2 = mongo.db.fs.chunks.find_one({"files_id": ff2['_id']})

    binary_img = io.BytesIO(fc['data'])
    binary_img2 = io.BytesIO(fc2['data'])
    base64_img = codecs.encode(binary_img.read(), 'base64')
    base64_img2 = codecs.encode(binary_img2.read(), 'base64')
    decoded_img = base64_img.decode('utf-8')
    decoded_img2 = base64_img2.decode('utf-8')

    return render_template("detail.html", data=results, img=decoded_img, img2=decoded_img2, setting=setting,userid=userid)


@app.route('/edit/<post_id>', methods=['POST', 'GET'])
def edit(post_id):
    user_id = session.get('userid', None)
    post = mongo.db.post
    before = post.find_one({"_id": ObjectId(post_id)})

    if request.method == "POST":
        title = request.form.get("title", type=str)
        body = request.form.get("body", type=str)
        keyword = request.form.get("keyword", type=str)
        f = request.files['file']
        f2 = request.files['file2']
        price = request.form.get("price", type=str)
        if title == "":
            flash("title is empty!")
            return render_template("edit.html", data=before)
        elif body == "":
            flash("body is empty!")
            return render_template("edit.html", data=before)
        elif keyword == "":
            flash("keyword is empty!")
            return render_template("edit.html", data=before)
        elif price == "":
            flash("Please input Price!!")
            return render_template("edit.html", data=before)
        elif not f:
            flash("Please upload Picture!")
            return render_template("edit.html", data=before)
        elif not f2:
            flash("Please upload Picture2!")
            return render_template("edit.html", data=before)
        else:
            fs = gridfs.GridFS(mongo.db)
            file_img_id = fs.put(f)
            file_img_id2 = fs.put(f2)

            post.update_one({"_id": ObjectId(post_id)}, {"$set": {"title": title}})
            post.update_one({"_id": ObjectId(post_id)}, {"$set": {"body": body}})
            post.update_one({"_id": ObjectId(post_id)}, {"$set": {"keyword": keyword}})
            post.update_one({"_id": ObjectId(post_id)}, {"$set": {"flies": file_img_id}})
            post.update_one({"_id": ObjectId(post_id)}, {"$set": {"flies2": file_img_id2}})
            post.update_one({"_id": ObjectId(post_id)}, {"$set": {"price": price}})

            return redirect("/")
    else:
        return render_template("edit.html", data=before,userid=user_id)


@app.route('/sold/<post_id>', methods=['POST', 'GET'])
def sold(post_id):
    user_id = session.get('userid', None)
    post = mongo.db.post
    post.update_one({"_id": ObjectId(post_id)}, {"$set": {"sold": "sold"}})
    return redirect("/")


@app.route('/following', methods=['POST', 'GET'])
def following():
    user_id = session.get('userid', None)
    username = request.args.get('username')
    followingList = mongo.db.signup.find_one({"username":username})["following"]
    print(followingList)
    return render_template("follow.html",data=followingList,userid=user_id)

@app.route('/follower', methods=['POST', 'GET'])
def follower():
    user_id = session.get('userid', None)
    username = request.args.get('username')
    username = request.args.get('username')
    followerList = mongo.db.signup.find_one({"username": username})["follower"]
    return render_template("follow.html",data=followerList,userid=user_id)


if __name__ == "__main__":
    app.run(host='127.0.0.1', debug=True, port=9999)