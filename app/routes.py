from app import app,mongo
from app.forms import LoginForm,RegisterForm
from bson.json_util import dumps
from flask import render_template,request,Response,json,redirect,flash,session,url_for
# from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import check_password_hash,generate_password_hash


classess = mongo.db['course']
collection = mongo.db['user']
enroll = mongo.db['enroll']



@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html",index =True)

@app.route("/courses")
@app.route("/courses/<term>")
def courses(term=None):
    if term is None:
        term = "spring 2019"
    classes = classess.find().sort([("courseID",+1)])
    return render_template("courses.html",courseData=classes,courses=True,term=term)

@app.route("/login",methods=['GET','POST'])    
def login():
    if session.get("first_name"):
        redirect('/index')
    form = LoginForm()
    if form.validate_on_submit():
        user = collection.find_one({"email":form.email.data})
        if user and check_password_hash(user['password'],form.password.data):
            flash(f"{user['first_name']},you are successfully logged in!","success")
            session['user_id']=user['id']
            session['first_name']=user['first_name']
            return redirect("/index")
        else:
            flash("sorry try again!","danger")
    return render_template("login.html",title="login",form=form, login=True)

@app.route("/register",methods=["GET","POST"])   
def register():
    if session.get("first_name"):
        redirect('/index')
    form = RegisterForm()
    if form.validate_on_submit():
        user_id = collection.count()
        user_id += 1
        email = form.email.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        password = generate_password_hash(password)
        collection.insert_one({"id":user_id,"first_name":first_name,"last_name":last_name,"email":email,"password":password})
        collection.save
        flash("You are successfully registered! ","success")
        return redirect("/index")
    return render_template("register.html",register=True,form=form)
    
@app.route("/enrollment",methods=["GET","POST"])   
def enrollment():
    if not session.get("first_name"):
        return redirect(url_for("login"))
    courseID = request.form.get("courseID")
    courseTitle = request.form.get("title")
    userID = session.get("user_id")
    if courseID:
        if enroll.find_one({"userID":userID,"courseID":courseID}):
            flash(f"Ooops you are already registred in this course {courseTitle}","danger")
            redirect("/courses")
        else:
            enroll.insert_one({"userID":userID,"courseID":courseID})
            flash(f"successfully registered in this course {courseTitle}","success")
    courseData = collection.aggregate(
                        [{
                            '$lookup': {
                                'from': 'enroll', 
                                'localField': 'id', 
                                'foreignField': 'userID', 
                                'as': 'r1'
                            }
                        }, {
                            '$unwind': {
                                'path': '$r1', 
                                'includeArrayIndex': 'r1_id', 
                                'preserveNullAndEmptyArrays': False
                            }
                        }, {
                            '$lookup': {
                                'from': 'course', 
                                'localField': 'r1.courseID', 
                                'foreignField': 'courseID', 
                                'as': 'r2'
                            }
                        }, {
                            '$unwind': {
                                'path': '$r2', 
                                'preserveNullAndEmptyArrays': False
                            }
                        }, {
                            '$match': {
                                'id': userID
                            }
                        }, {
                            '$sort': {
                                'courseID': +1
                            }
                        }]
    )
    # print(courseData)   
    return render_template("enrollment.html",enrollment=True,title="Enrollment",courseData=courseData)
    
# @app.route("/api")
# @app.route("/api/<idx>")
# def api(idx=None):
#     if(idx==None):
#         data = courseData
#     else:
#         data = courseData[int(idx)]
#     return Response(json.dumps(data),mimetype="application/json")


@app.route("/users")
def users():
    query = collection.find()
    # print(dumps(query))
    return render_template('users.html',users=query)

@app.route("/logout")
def logout():
    session['user_id']=None
    session.pop("first_name",None)
    return redirect(url_for('index'))