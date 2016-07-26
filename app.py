#!/usr/bin/env python

from flask import Flask
from flask import url_for, redirect, request, make_response
from flask import escape, session
from flask import flash
from flask import render_template
from app_config import app_secret_key
from app_util import cookie_check
from input_check import *
from call_by_app import *
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


app = Flask(__name__)
app.secret_key = app_secret_key

@app.route("/")
def welcome():
    is_login = cookie_check()
    if is_login == True:
        # when user has a cookie, login if the cookie is correct
        return redirect(url_for("log_in_auth"))
        #return render_template("welcome.html")
    else:
        # when cookie is not correct or no cookie, go welcome page
        return render_template("welcome.html")


@app.route("/signupauth", methods=["POST"])
def sign_up_auth():
    # Check the input, if not correct, show error info
    if not validate_email(request.form["email"]):
        flash("Your email is not valid. Please check the input.")
        return redirect(url_for("welcome"))
    if not validate_username(request.form["username"]):
        flash("Your user name is not valid. Please check the input.")
        return redirect(url_for("welcome"))
    if not validate_nickname(request.form["nickname"]):
        flash("Your nickname is not valid. Please check the input.")
        return redirect(url_for("welcome"))
    if not validate_phone(request.form["phone"]):
        flash("Your phone number is not valid. Please check the input.")
        return redirect(url_for("welcome"))
    if not validate_gender(request.form["gender"]):
        flash("Your please select your gender.")
        return redirect(url_for("welcome"))
    if not validate_facebook(request.form["facebook"]):
        flash("Please provide you facebook link. Start with https://www.facebook.com/")
        return redirect(url_for("welcome"))
    if not validate_str_equal(request.form["password"], request.form["cpassword"]):
        flash("Password not match. Try again.")
        return redirect(url_for("welcome"))

    # TODO: Add the user to database
    username = request.form["username"]
    nickname = request.form["nickname"]
    password = request.form["password"]
    phone = request.form["phone"]
    gender = request.form["gender"].lower()
    email = request.form["email"]
    facebook = request.form["facebook"]
    if not add_user( username, nickname, password, phone, gender, email, facebook):
        flash("Your account already exists in our system")
        return redirect(url_for("welcome"))
    else:
        #resp = redirect(url_for("dashboard"))
        resp = make_response(render_template("dashboard.html"))
        resp.set_cookie("username", username)
        resp.set_cookie("password", password)
        return resp



@app.route("/loginauth", methods=["POST","GET"])
def log_in_auth():
    is_login = cookie_check()
    if is_login == True:
        # if user has correct cookie, go to dashboard page
        return redirect(url_for("dashboard"))
    elif is_login == False:
        # inform the user that the session has expired
        flash("Your information is not in our database.")
        return redirect(url_for("welcome"))
    else:
        # If the user doesn't have a cookie, it must have filled the form
        if not validate_email(request.form["email"]):
            flash("Your email is not valid. Please check the input.")
            return redirect(url_for("welcome"))

        # Set cookie if the user could login
        print "GOT EMAIL ::" + request.form["email"] +"\n"
        print "GOT PASSWORD ::" + request.form["password"] +"\n"

        can_login, username, password = check_user(request.form["email"], request.form["password"])
        if can_login:
            #resp = redirect(url_for("dashboard"))
            s = session
            s.username = username
            print "SET USERNAME :: " + str(username) +"\n"
            print "SET PASSWORD :: " + str(password) +"\n"
            s.password = password
            #if s.setSession:
            #resp = make_response(render_template("dashboard.html"))
            resp = make_response(redirect('/dashboard'))
            resp.set_cookie("username", username)
            resp.set_cookie("password", password)
            #resp.set_cookie('session_id', s.session_id)
            print "coockie setted"
            return resp
        else:
            flash("Your email or password is not in our database.")
            return redirect(url_for("welcome"))


@app.route("/dashboard", methods=["GET"])
def dashboard():

    is_login = cookie_check()
    if not is_login:
        flash("not logged in")
        return redirect(url_for("welcome"))

    # TODO: need to get a lot of info from database
    # 1) get current userid

    userid = request.cookies.get("username")
    friendid = ""
    matched_person = {}  # a dict, keys = ["id", "name", "gender", "phone", "facebook"]
    recommend_restaurants = []  # a list, each is a dict, keys = ["name", "address", "star"]

    # 2) first know if there is any pending match
    pending_flag, matched_person1 = check_match(userid)

    # 3) second check recommendation
    # attention, matched_person would be empty if both 1&2 is empty
    matched_person2, recommend_restaurants = check_recommendation(userid)

    # 4) merge the result of matched_person
    if bool(matched_person1) or bool(matched_person2):
        if bool(matched_person1):
            matched_person = matched_person1
            friendid = matched_person1["id"]
        else:
            matched_person = matched_person2
            friendid = matched_person2["id"]
    else:
        matched_person = {}

    _status = pending_flag  # THIS IS A BOOLEAN VALUE that if True-> enable accept/decline
                            # if false -> disable accept/decline
    figure = maptofigure(userid)
	
    return render_template("dashboard.html", person=matched_person,
                           restaurants=recommend_restaurants,
                           status=_status,
						   avatar = figure) # ADD friendid as a variable that won't display


@app.route("/newproposal", methods=["POST"])
def new_proposal():
    # Only works when user login
    is_login = cookie_check()
    if is_login:
        # The following data will be collected here
        # request.form["date"]  xxxx-xx-xx
        # request.form["starthour"]
        # request.form["startmin"]
        # request.form["endhour"]
        # request.form["endmin"]
        # request.form["foodtype"]
        # request.form["distance"]
        # request.form["budget"]
        # request.form["gender"]
        if not validate_date(request.form["date"]):
            flash("Your appointment date is not valid. Please check the input.")
            return redirect(url_for("dashboard"))
        if not validate_hour(request.form["starthour"]):
            flash("Your appointment start hour is not valid. Please check the input.")
            return redirect(url_for("dashboard"))
        if not validate_minute(request.form["startmin"]):
            flash("Your appointment start minute is not valid. Please check the input.")
            return redirect(url_for("dashboard"))
        if not validate_hour(request.form["endhour"]):
            flash("Your appointment end hour is not valid. Please check the input.")
            return redirect(url_for("dashboard"))
        if not validate_minute(request.form["endmin"]):
            flash("Your appointment end minute is not valid. Please check the input.")
            return redirect(url_for("dashboard"))
        if not validate_empty_str(request.form["foodtype"]):
            flash("Your didn't select the perferred food type")
            return redirect(url_for("dashboard"))
        if not validate_gender(request.form["gender"]):
            flash("Your preferred gender is not valid. Please check the input.")
            return redirect(url_for("dashboard"))

        # TODO: handle in database
        userid = request.cookies.get("username")

        date = request.form["date"]
        starthour = request.form["starthour"]
        startmin = request.form["startmin"]
        endhour = request.form["endhour"]
        endmin = request.form["endmin"]
        foodtype = request.form["foodtype"].lower()
        distance = request.form["distance"]
        budget = request.form["budget"]
        gender = request.form["gender"].lower()
        latitude = request.form["latitude"] ##----string value
        longitude = request.form["longitude"] ##----string value

	print "GET lati ::" + request.form["latitude"] +"\n"
	print "GET longi ::" + request.form["longitude"] +"\n"

        add_proposal(userid, date, starthour, startmin, endhour, endmin,
                     foodtype, distance, budget, gender, latitude, longitude)

	return redirect(url_for("dashboard"))
    else:
        #flash("404 Page Not Found")
        flash("not logged in")
        return redirect(url_for("welcome"))


@app.route("/acceptproposal", methods=["GET"])
def accept_proposal():
    is_login = cookie_check()
    if not is_login:
        flash("not logged in")
        return redirect(url_for("welcome"))
    else:
        pass
    # The ID of accepted user is passed in URL
    userid = request.cookies.get("username")
    # The ID of accept user should be get in cookie
    friendid = request.args.get("friendid")
    accept_match(userid, friendid)
    flash("Have accepted the proposal!")
    return redirect(url_for("dashboard"))


@app.route("/declineproposal", methods=["GET"])
def decline_proposal():
    is_login = cookie_check()
    if not is_login:
        flash("not logged in")
        return redirect(url_for("welcome"))
    else:
        pass
    # The ID of declined user is passed in URL
    userid = request.cookies.get("username")
    # The ID of decline user should be get in cookie
    friendid = request.args.get("friendid")
    decline_match(userid, friendid)
    flash("Have declined the proposal!")
    return redirect(url_for("dashboard"))


@app.route("/profile", methods=["GET"])
def profile():
    is_login = cookie_check()
    if not is_login:
        flash("not logged in")
        return redirect(url_for("welcome"))
    else:
        pass
    # Assume we have the following variables resolved
    _user_name = request.cookies.get("username")
    print "get username: " + str(_user_name)
    profile = get_user_info(_user_name)

    _nick_name = profile['nickname']
    _email = profile['email']
    _phone = profile['phone']
    _gender = profile['gender']
    _facebook = profile['facebook']
	
    figure = maptofigure(_user_name)

    return render_template("profile.html",
                           username = _user_name,
                           nickname = _nick_name,
                           email = _email,
                           phone = _phone,
                           gender = _gender,
                           facebook = _facebook,
						   avatar = figure)


@app.route("/updateprofile", methods=["POST"])
def update_profile():
    pass


@app.route("/updatepassword", methods=["POST"])
def update_password():
    pass


# TODO: add the link to this function to login page
@app.route("/forgetpassword", methods=["POST"])
def forget_password():
    pass


@app.route("/logout", methods=["GET"])
def logout():
    # Remove the cookie
    resp = make_response(redirect('/'))
    resp.set_cookie("username", "", expires = 0)
    resp.set_cookie("password", "", expires = 0)
    return resp

def maptofigure(S):
    line = "https://s3.amazonaws.com/cse6242d5/d5/"
    X = 0
    for each in S:
        X = X+ ord(each)

    x = X % 100
    line = line +str(x) +".png"
    return line

if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True)


