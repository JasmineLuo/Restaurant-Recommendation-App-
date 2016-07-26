import json
import string
import psycopg2
import sys
import datetime
import time
import math
import urllib, hashlib
import shutil
import requests
import os.path
import numpy as np
from pprint import pprint
from random import randint
from is_match import *
from append_predict_matrix import *

## container of login & signup functions

# function1:-----------------
# @app.route("/signupauth", methods=["POST"])
# call by def sign_up_auth():
    # The following data will be collected here
    # request.form["email"]
    # request.form["username"]
    # request.form["nickname"]
    # request.form["phone"]
    # request.form["gender"]
    # request.form["password"]
    # request.form["cpassword"]  i.e. confirmed password
    # also the facebook link will be put into the column ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~NOTICE!!!

def add_user( username, nickname, password, phone, gender, email, facebook):
	## assume the password has been confirmed
	flag = False
	
	userID = username
	userNAME = nickname
	passWORD = password
	#cpassWORD = cpassword
	PHONE = phone
	GENDER = gender
	EMAIL = email
	size =400

	con=None
	try:
     
		con = psycopg2.connect("dbname='testdb' user='postgres'")   
		cur = con.cursor()
		#create table and all the rest table
		cur.execute("SELECT * FROM USER_INFO WHERE USERID = %s; ", (userID,))
		result1 = cur.fetchall()
		#con.commit()
		#print len(str(result1))
		cur.execute("SELECT * FROM USER_INFO WHERE EMAIL = %s; ", (EMAIL,))
		result2 = cur.fetchall()
		con.commit()
		#print len(str(result2))
		if (len(str(result1))<3) and (len(str(result2)) <3):
			# the userID and user email must be unique
			flag=True
			#handle insert
			#step 1 insert			
			cur.execute("INSERT INTO USER_INFO VALUES( %s, %s, %s, %s, %s, %s, %s, %s, %s)",(userID, userNAME, passWORD, 
				PHONE, EMAIL, GENDER, 0, 0, facebook ))
			con.commit()
			append_predict_matrix()
			# default for ave_star, Review_num and facebook link is 0,0 and None

			#step 2 default avatar
			#rel_path = "user_image/"+userID+".png"
			#Token= "cse6242D5"+EMAIL
			#gravatar_url = "http://www.gravatar.com/avatar/" + hashlib.md5(Token.lower()).hexdigest() + "?"
			#gravatar_url += urllib.urlencode({'d': "identicon",'s':str(size)})
			#urllib.urlretrieve(gravatar_url, rel_path)
			#print "new avatar added!"
            ### should also be able to send to S3 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~NOTICE!
		else:
			flag=False
	        con.commit()

	except psycopg2.DatabaseError, e:
		if con:
        		con.rollback()
    		print 'Error %s' % e    
    		sys.exit(1)
	finally:
    
		if con:
			con.close()
# return boolean value whether the user already exsists

	return  flag





# function2:-----------------
# @app.route("/loginauth", methods=["POST"])
# call by def log_in_auth():
    # The following data will be collected here
    # request.form["email"]
    # request.form["password"]

def check_user( email, password):
	
	flag = False
	
	EMAIL = email
	passWORD = password
	userid = None

	con=None
	try:
     
		con = psycopg2.connect("dbname='testdb' user='postgres'")   
		cur = con.cursor()
		#create table and all the rest table
		cur.execute("SELECT USERID FROM USER_INFO WHERE EMAIL = %s AND PASSWORD = %s;", (EMAIL,passWORD))
		result1 = cur.fetchall()
		con.commit()

		if len(str(result1)) >3:
		# the userID and user email must be unique
			flag=True
			for row in result1:
				userid = row[0]
			# handle insert
			# ------------------------- display format of the result?
			# default for ave_star, Review_num and facebook link is 0,0 and None
		else:
			flag=False

	        con.commit()

	except psycopg2.DatabaseError, e:
		if con:
        		con.rollback()
    		print 'Error %s' % e    
    		sys.exit(1)
	finally:
    
    		if con:
       			 con.close()
# return boolean value whether the user login info is right
	return  flag,userid,passWORD


#function 3.1.1 :---------------------
#call when the accecpt match is clicked
def accept_match(userid, friendid):
    #means current userid has accepted
    con = None

    try:
		con = psycopg2.connect("dbname='testdb' user='postgres'")   
		cur = con.cursor()
        # if host is user id:
		cur.execute("SELECT * FROM USER_CONNECTION WHERE USERID = %s AND FRIENDID = %s",(userid, friendid))
		result1=cur.fetchall()
		con.commit()
		if len(str(result1)) >3:
			#print "executed 1"
			for row in result1:
				if row[3] == "PENDING_H":
                    # now the item can be removed since both of them accpeted
					cur.execute("DELETE FROM USER_CONNECTION WHERE USERID = %s AND FRIENDID = %s", (userid, friendid))
                    # trigger recommendation algorithm ~~~~~~~~~~~~~~~~~~~~~~~~~~NOTICE ! IN function 6
					con.commit()
					#print "find_recommendation(userid, friendid)"
					find_recommendation(userid, friendid) # no return only write to database
				elif row[3] == "PENDING_A":
                    # status change
					cur.execute("UPDATE USER_CONNECTION SET STATUS = %s WHERE USERID = %s AND FRIENDID = %s "
                        +"AND STATUS = %s", ("PENDING_F", userid, friendid, "PENDING_A"))
					con.commit()
				else:
					#print row[3] + "unexpected"
					pass
		else:
			pass

        # if host is friend id:  
		cur.execute("SELECT * FROM USER_CONNECTION WHERE USERID = %s AND FRIENDID = %s",(friendid, userid))
		result2=cur.fetchall()
		con.commit()
		if len(str(result2)) >3:
			#print "executed 2"
			for row in result2:
				if row[3] == "PENDING_F":
                    # now the item can be removed since both of them accpeted
					cur.execute("DELETE FROM USER_CONNECTION WHERE USERID = %s AND FRIENDID = %s", (friendid,userid))
					con.commit()
                    # trigger recommendation algorithm ~~~~~~~~~~~~~~~~~~~~~~~~~~NOTICE ! IN function 6
					#print find_recommendation(friendid,userid)
					find_recommendation(friendid,userid)
				elif row[3] == "PENDING_A":
                    # status change
					#print str(friendid)
					cur.execute("UPDATE USER_CONNECTION SET STATUS = %s WHERE (USERID = %s AND FRIENDID = %s "
                        +"AND STATUS = %s);", ("PENDING_H", friendid, userid, "PENDING_A"))
					con.commit()
				else:
					#print row[3] + "unexpected"
					pass
		else:
			pass
    
		con.commit()
    except psycopg2.DatabaseError, e:
		if con:
        		con.rollback()
			print 'Error %s' % e    
			sys.exit(1)
    finally:
    		if con:
       			 con.close()

    return

#function 3.1.2: -------------------
#process when the decline is clicked
def decline_match(userid, friendid):
    
    con = None
    
    try:
		con = psycopg2.connect("dbname='testdb' user='postgres'")   
		cur = con.cursor()      ###~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~NOTICE in finding matches not to recommend this user again
        # set to blacklist
        # blackby = time.strftime("%H:%M:%S") + datetime.timedelta(minutes = 20)
		cur.execute("UPDATE USER_CONNECTION SET STATUS = %s, TIMER = %s WHERE USERID = %s AND FRIENDID = %s",
                ("BLACKLIST", None, userid, friendid))
		cur.execute("UPDATE USER_CONNECTION SET STATUS = %s, TIMER = %s WHERE USERID = %s AND FRIENDID = %s",
                ("BLACKLIST", None, friendid, userid))
        # return the two post to unmatched
		cur.execute("UPDATE USER_POST SET STATUS = %s WHERE USERID = %s AND STATUS = %s", 
                ("unmatched", userid, "matched"))
		cur.execute("UPDATE USER_POST SET STATUS = %s WHERE USERID = %s AND STATUS = %s", 
                ("unmatched", friendid, "matched"))
		
		# enable to find match
		cur.execute("SELECT * FROM USER_POST WHERE USERID = %s AND STATUS = %s", (userid, "unmatched"))
		result1 = cur.fetchall()
		con.commit()
		for row1 in result1:
			#print str(row1[0])
			find_match(row1[0], userid)

		cur.execute("SELECT * FROM USER_POST WHERE USERID = %s AND STATUS = %s", (friendid, "unmatched"))
		result2 = cur.fetchall()
		con.commit()
		for row2 in result2:
			#print friendid + " further find " + str(row2[0])
			find_match(row2[0], friendid)

		con.commit()
    except psycopg2.DatabaseError, e:
	    if con:
        		con.rollback()
			print 'Error %s' % e    
			sys.exit(1)
    finally:
    		if con:
       			 con.close()
    return





#function 3.1 :---------------------
#possibility A: call by function 3 to handle before insert new post
# --------@app.route("/newproposal", methods=["POST"])
# -------function 3 -call by def new_proposal():
#possibility B: call by user request at certian interval
def check_match(userid):  ## form match should be called only when posted

	Token = "prepared"
	friendid = None
	matched_person = {}
	pending_flag = False
	con =None
	try:
     
		con = psycopg2.connect("dbname='testdb' user='postgres'")
		cur = con.cursor()

        # NOTICE: the user who has both recived match will be removed from the list
        # When Both Agree to match -> run recommendation -> post the list to the user -> clear from connection table
        # and status in POST also cleared ~~~~~~~~~~~~~~~-> new event in EVENT?

        ####---first clear all expired pending
        # clean in the connection table
		#current_time = time.strftime("%H:%M:%S")
		current_time = datetime.datetime.now().strftime("%H:%M:%S")
		#print current_time
		cur.execute("UPDATE USER_CONNECTION SET STATUS = %s, TIMER = %s WHERE TIMER IS NOT NULL AND TIMER <= %s",
                ( "END",None, current_time))
		con.commit()
        
        #### ---second check if the user is between selected by algorthm & accept match
		cur.execute("SELECT * FROM USER_CONNECTION WHERE (USERID = %s OR FRIENDID = %s) AND STATUS <> %s", (userid, userid,"BLACKLIST"))
		result = cur.fetchall()
		con.commit()
		if len(str(result)) <3:
            # not in connection table
			print "end1\n"
			return pending_flag,{} ## either not selected by algorithm or haven formed match
		else:
			pass # do the following

        #### ----third check if the suggested match is expired
		cur.execute("SELECT * FROM USER_CONNECTION WHERE (USERID = %s OR FRIENDID = %s) and STATUS = %s", (userid, userid, "END"))
		result = cur.fetchall()
		con.commit()
		if len(str(result)) >3:
            # already expired
			for row in result:
                #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~POP UP TO USR ?????~~~~~~~~~~~~~~~~~~~no pop
				if row[1] == userid:
                    #remove from connection one:
					cur.execute("DELETE FROM USER_CONNECTION WHERE USERID = %s and STATUS = %s", (userid, "END"))
                    #back to unmatched in post
					cur.execute("UPDATE USER_POST SET STATUS = %s WHERE USERID = %s and STATUS = %s", 
                        ("unmatched", userid, "matched"))
					cur.execute("UPDATE USER_POST SET STATUS = %s WHERE USERID = %s and STATUS = %s", 
                        ("unmatched",row[2], "matched"))
					con.commit()
                    #this is why the accpeted match should be removed, otherwise will all become "unmatch" in this operation
					pass
				else:
					cur.execute("DELETE FROM USER_CONNECTION WHERE FRIENDID = %s and STATUS = %s", (userid, "END"))
                    #back to unmatched in post
					cur.execute("UPDATE USER_POST SET STATUS = %s WHERE USERID = %s and STATUS = %s", 
                        ("unmatched", userid, "matched"))
					cur.execute("UPDATE USER_POST SET STATUS = %s WHERE USERID = %s and STATUS = %s", 
						("unmatched",row[1], "matched"))
					con.commit()
					pass				
					#return pending_flag,{}
                    #this is why the accpeted match should be removed, otherwise will all become "unmatch" in this operation
		else:
			pass
        

        ####--- forth check if there is a pending for current user id
        ####--- if so find the friend id
		cur.execute("SELECT * FROM USER_CONNECTION WHERE (USERID = %s AND STATUS = %s)"
                +" OR (FRIENDID = %s AND STATUS = %s) "
                +" OR (STATUS = %s)", (userid, 'PENDING_H',userid, 'PENDING_F', "PENDING_A"))
		result = cur.fetchall()
		con.commit()

		if len(str(result)) >3 :
            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~return to the user matched list!
			pending_flag = True
			for row in result:
				if row[1] == userid:
					friendid = row[2]
				else:
					friendid = row[1]
				#~~~~~~~~~~~~~~~~~~get info of this friendid
				cur.execute("SELECT * FROM USER_INFO WHERE USERID = %s",(friendid,))
				result5 = cur.fetchall()
				con.commit()
				matched_person = {"id":"","name": "", "gender":"", "phone":"", "facebook":""};
				for row in result5:
					matched_person["id"] = row[0]
					matched_person["name"] = row[1]
					matched_person["gender"] = row[5]
					matched_person["phone"] = row[3]
					matched_person["facebook"] = row[8]
				return pending_flag, matched_person
		else:
            #### ---- check if is waiting for another user's pending
			cur.execute("SELECT * FROM USER_CONNECTION WHERE (USERID = %s AND STATUS = %s)"
                +" OR (FRIENDID = %s AND STATUS = %s)", (userid, 'PENDING_F',userid, 'PENDING_H'))
			check = cur.fetchall()
			con.commit()
			if len(str(check)) >3:
				pending_flag = False # the other guy is pending
				for row in check:
					if row[1] == userid:
						friendid = row[2]
					else:
						friendid = row[1]
				#~~~~~~~~~~~~~~~~~~get info of this friendid
				#print friendid
				cur.execute("SELECT * FROM USER_INFO WHERE USERID = %s",(friendid,))
				result5 = cur.fetchall()
				con.commit()
				matched_person = {"id":"","name": "", "gender":"", "phone":"", "facebook":""};
				for row in result5:
					matched_person["id"] = row[0]
					matched_person["name"] = row[1]
					matched_person["gender"] = row[5]
					matched_person["phone"] = row[3]
					matched_person["facebook"] = row[8]
				return pending_flag, matched_person
			else:
                #able to continue the matching process
				pass

			con.commit()
		
	except psycopg2.DatabaseError, e:
		if con:
        		con.rollback()
			print 'Error %s' % e    
			sys.exit(1)
	finally:
			if con:
 				con.close()

	return False, {}


###~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~temp function 
#def ifmatch (ida, idb):
#	return True


#function 3.2 :---------------------
# call by function 3 to handle after insert new post
# --------@app.route("/newproposal", methods=["POST"])
# this won't post anything to the board, the user need to check by himself
def find_match(postID, userID):
    ### this function is to find a possible match for current post
    ### should be called right after a new post is formed
	con = None
	friendid = None
    
	try: 
		con = psycopg2.connect("dbname='testdb' user='postgres'")   
		cur = con.cursor()

		##################fetch the gender of user#######################
		cur.execute("SELECT GENDER FROM USER_INFO WHERE USERID = %s", (userID,))
		reference_gender=cur.fetchall()
		reference_gender=reference_gender[0][0]
        
        # can also do some filtering here
		cur.execute("SELECT * FROM USER_POST WHERE POSTID <> %s AND USERID <> %s AND STATUS = %s", (postID, userID, "unmatched"))
		candidates = cur.fetchall() # all possible candidates

		cur.execute("SELECT * FROM USER_POST WHERE POSTID = %s AND USERID = %s AND STATUS = %s", (postID, userID, "unmatched"))
		reference = cur.fetchone() # origin post
		con.commit()

		for each in candidates:
			###~~~~~~~~~~~~~~~~~~~~~~~~call the algorithm function~~~~~~~~~~~~~return boolean value
			##################fetch the gender of user#######################
			cur.execute("SELECT GENDER FROM USER_INFO WHERE USERID = %s", (each[1],))
			each_gender=cur.fetchall()
			each_gender=each_gender[0][0]
			con.commit()

			#pos1 = ifmatch(each, reference)
			pos1 = is_match(reference, each, reference_gender, each_gender)
			#print "pos1:: " +str(pos1)+"\n"
			pos2 = True
            
			#print each[1] # for test
			cur.execute("SELECT * FROM USER_CONNECTION WHERE ((USERID = %s AND FRIENDID = %s) "
                +"OR (USERID = %s AND FRIENDID = %s)) AND STATUS = %s", (userID, str(each[1]), str(each[1]), userID, "BLACKLIST"))
			result = cur.fetchall()
			con.commit()

			if len(str(result)) <3:
				pos2 = True
			else:
				pos2 = False
             
            # pos1 means the two user match
            # pos2 means the two user hasn't decline each other before

			if pos1 and pos2:
                #update post status
				cur.execute("UPDATE USER_POST SET STATUS = %s WHERE (POSTID = %s OR POSTID = %s) AND STATUS = %s",
                    ("matched", postID, each[0],"unmatched"))
				con.commit()
				print "added a match!"
				#print "host:" + str(postID) + "friend" + str(each[0])
                #add to the connection table
                #calculate the best by data
				#bestby = bestby.strftime("%H:%M:%S")
                #add an interval
				bestby = datetime.datetime.now() + datetime.timedelta(minutes = 30)
				bestby = bestby.strftime("%H:%M:%S")
				###~~~~~~~~~~~~~~~~~~~~~~~~~~~~should be answered within 20 minutes
				cur.execute("INSERT INTO USER_CONNECTION(USERID, FRIENDID, STATUS, TIMER) VALUES(%s, %s, %s, %s)",
					(userID, each[1],"PENDING_A",bestby))
				friendid = each[1]    
				con.commit()            
                #notice, con_ID serial
				break # the following of the list won't be checked
			else:
				pass
        
		con.commit()
	except psycopg2.DatabaseError, e:
		if con:
			con.rollback()
			print 'Error %s' % e    
			sys.exit(1)
	finally:
    
			if con:
				con.close()
    
	return  str(friendid) ###~~~~~~~~~~~~~~~~~~~~~~~~~~~~~just for test



# function3:-----------------
# @app.route("/newproposal", methods=["POST"])
# call by def new_proposal():
# request.form["date"]
# request.form["starthour"]
# request.form["startmin"]
# request.form["endhour"]
# request.form["endmin"]
# request.form["foodtype"]
# request.form["distance"]
# request.form["budget"]
# request.form["gender"]

def add_proposal( userid, date, starthour, startmin, endhour, endmin, foodtype, distance, budget, gender, latitude, longitude):
	# assume the userid can be obtained 
	flag = False
	
	#bind time info to database format
	userID = userid
	print "Obtained latitude ::" + latitude +"\n"
	print "Obtained longitude ::" + longitude +"\n"
	print "Obtained radiuc ::" + distance +"\n"
	print "Obtained price ::" + budget +"\n"
	print "Obtained category ::" + foodtype +"\n"
	LATI = 	float(latitude)
	LONGI = float(longitude)
	TYPE = foodtype
	RADIUS = float(distance)
	#how to deal with this?
	PRICE = float(budget) # value:1~4
	GENDER = gender
	STATUS = "unmatched"
	
	#FIRST, date format:
	#should be in "year-month-date"
	if '-' in date:
		DATEE = date
	else:
		year = date.split(' ')[0]
		month = date.split(' ')[1]
		day = date.split(' ')[2]
		# here I assume the formate as split by " ", could be other token
		DATEE = year +"-"+ month + "-" + day
	
	#SECOND, time format
	#shoud be in "hh:mm:ss"
	# (1 make sure they are all 2 digit
	if len(starthour)<2:
		starthour = "0"+starthour
	else:
		pass
	if len(startmin)<2:
		startmin = "0"+startmin
	else:
		pass
	if len(endhour)<2:
		endhour = "0"+endhour
	else:
		pass
	if len(endmin)<2:
		endmin = "0"+endmin
	else:
		pass

	startTIME = starthour +":" +startmin +":00"
	endTIME = endhour +":" + endmin +":00"

	# Third, GENERATE KEY FOR POSTID
	# combine userID and current time
	postime = datetime.datetime.now().strftime("%Y-%m-%d-%H")#~~~~~~~~~~~~~~~~~can post every one hour 
	postID = userID+"::"+postime

	con=None
	try:
     
		con = psycopg2.connect("dbname='testdb' user='postgres'")   
		cur = con.cursor()
		
		# content of table:
		#cur.execute("CREATE TABLE IF NOT EXISTS USER_POST ( POSTID VARCHAR(45) PRIMARY KEY ,USERID VARCHAR(45) NOT NULL,"+
		#"REFERENCES USER_INFO(USERID) ON DELETE CASCADE, START_TIME TIME, END_TIME TIME,"+
		#"LATITUDE FLOAT, LONGITUDE FLOAT,"+
		#"RADIUS FLOAT, PRICE FLOAT, GENDER VARCHAR(10), TYPE VARCHAR(120), DATEE DATE,"+
		#"STATUS VARCHAR(15) )")
                
		cur.execute("SELECT * FROM USER_POST WHERE POSTID = %s OR (USERID = %s AND STATUS = %s);", (postID,userID, "unmatched"))
		result1 = cur.fetchall()
		con.commit()

		if len(str(result1)) <3:
		    # the post can't be gengerated by same user at the same time
			flag=True
			# handle insert
			cur.execute("INSERT INTO USER_POST VALUES( %s, %s, %s, %s, %s, %s,"+
				" %s, %s, %s, %s, %s, %s);", (postID, userID, startTIME, endTIME, LATI, LONGI, RADIUS, PRICE, GENDER, 					TYPE, DATEE,STATUS ))
			con.commit()
            ### form_mateches~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~???
			find_match(postID, userID)  ### find mateches for this post id
		else:
			flag=False
	        con.commit()

	except psycopg2.DatabaseError, e:
		if con:
        		con.rollback()
    		print 'Error %s' % e    
    		sys.exit(1)
	finally:
    
    		if con:
       			 con.close()
	# return value when insertion failed, for instance the user post two event in one second...
	return  flag




# function4:-----------------
#@app.route("/dashboard", methods=["GET"])
#call by def dashboard():
def get_info_dashboard (userid):
	# get info for current user
	
	flag = False
	INFO=""
	token = "pending"

	con = None
	
	try:
     
		con = psycopg2.connect("dbname='testdb' user='postgres'")   
		cur = con.cursor()
		# get info after connection
		userID=userid

		#First, get avatar:
		imageNAME = "user_image/"+ userID +".png"
		INFO = INFO + imageNAME +"\n"		

		#Second, get other current appointment info
		#"CREATE TABLE IF NOT EXISTS EVENT (EVENT_ID VARCHAR(45) PRIMARY KEY, USERID_A VARCHAR(45)"+
		#"REFERENCES USER_INFO(USERID) ON DELETE CASCADE,"+
		#"USERID_B VARCHAR(45) REFERENCES USER_INFO(USERID) ON DELETE CASCADE,"+
		#"BUSINESS_ID VARCHAR(90) REFERENCES BUSINESS(ID) ON DELETE CASCADE,"+
		#"MEET_TIME TIME, MEET_DATE DATE, STATUS VARCHAR(15))"		
		cur.execute("SELECT * FROM EVENT INNER JOIN BUSINESS ON EVENT.BUSINESS_ID = BUSINESS.ID"
				+" WHERE USERID_A = %s OR USERID_B = %s AND STATUS = %s",(userID, userID, token))
		result1 = cur.fetchall()
		con.commit()
		if result1 is not None:
			flag = True
			#send back all pending appointment info
			## ---------------------IN WHAT FORMAT?
			for row in result1:
				INFO = INFO + row['USERID_A'][1] + "\t"
				INFO = INFO + row['USERID_B'][1] + "\t"
				INFO = INFO + row['NAME'][1] + "\t"
				INFO = INFO + row['ADDRESS'][1] + "\t"
				INFO = INFO + row['MEET_TIME'][1] + "\t"
				INFO = INFO + row['MEET_DATE'][1] + "\t"
				INFO = INFO + "\n"
		else:
			flag = False

		con.commit()
	except psycopg2.DatabaseError, e:
		if con:
        		con.rollback()
    		print 'Error %s' % e    
    		sys.exit(1)
	finally:
    
    		if con:
       			 con.close()
	return str(flag) + "\n"+ INFO






#function5:------------------
#@app.route("/profile", methods=["GET"])
#def profile():

def get_user_info (userid):
	
	INFO = ""
	userID = userid
	profile = {'nickname':'', 'email':'', 'phone':'', 'gender':'', 'facebook':''}

	#imageNAME = "user_image/"+ userID +".png"
	#INFO = INFO + imageNAME +"\n"

	con = None
	try:
     
		con = psycopg2.connect("dbname='testdb' user='postgres'")   
		cur = con.cursor()		
		cur.execute("SELECT * FROM USER_INFO WHERE USERID = %s;", (userID,))
		## this must exists since the login has been done
		result1 = cur.fetchall()
		con.commit()
		## output format? 
		for row in result1:
			profile['nickname'] = row[1] # username
			profile['email'] = row[4] # email
			profile['phone'] = row[3] # phone
			profile['gender'] = row[5] # gender
			profile['facebook'] = (row[8]) # facebook

		con.commit()
	
	except psycopg2.DatabaseError, e:
		if con:
        		con.rollback()
    		print 'Error %s' % e    
    		sys.exit(1)
	finally:
    
    		if con:
       			 con.close()

	return profile


#~~~~~~~~~~~~~~~~~~~~~~~only a test function for function6:
#def get_recommendation(userA_index, userB_index, business_index):
#	return business_index
#def get_sub_recommendation(userA_index, userB_index):
#	return None

#################################### form algorithm
def match_pair(user_a, user_b, bus_list, rating_matrix):
    recomm_list = []
    ratings_a = []
    ratings_b = []
    
    #retrieve ratings from user rating matrix
    for bus in bus_list:
        rating_a = rating_matrix[user_a][bus]
        rating_b = rating_matrix[user_b][bus]
        if rating_a >= rating_b:
            recomm_list.append([bus, rating_b])
        else:
            recomm_list.append([bus, rating_a])

    #merge ratings based on the lower rating
    recomm_list.sort(key=lambda tup: tup[1], reverse=True)
    recomm_arr = np.array(recomm_list)
    recomm_list = recomm_arr[:,0].tolist()
    #print "recomm_list: ", recomm_list        
    return recomm_list
####################################### end

#function 6:--------------------------
#called after a match is accpected on both side
#no output, only write to database

def find_recommendation(userid, friendid):

	###################################### LOAD matrix
	pred_rating = np.load("baseline_matrix.npy")	

	con = None

	try:
		con = psycopg2.connect("dbname='testdb' user='postgres'")   
		cur = con.cursor()
		#1, do filtering
		#Filtering is base on 
		#1-1: pricerange in business_attribute
		#1-2: coarse selection of latitude and longitude in business
		#1-3: category and type match
		#1-4: no time to consider weekday =_=
		cur.execute("SELECT * FROM USER_POST WHERE USERID = %s AND STATUS = %s", (userid, "matched"))
		result1 = cur.fetchall()
		con.commit()
		for row in result1:
			start_time = row[2]
			price = row[7]
			cat = row[9]
			datee = row[10] # only consider this guy since they won't be matched if they are different

			lat_a = row[4]
			lon_a = row[5]
			r_a = row[6]  #---km unit
			xmin_a = lon_a-r_a/(111.320*math.cos(lat_a/180*math.pi)) -0.01 # padding for the inacuracy
			xmax_a = lon_a+r_a/(111.320*math.cos(lat_a/180*math.pi)) +0.01
			ymin_a = lat_a-r_a/110.574 - 0.01
			ymax_a = lat_a+r_a/110.574 + 0.01
			print "LongMIN_A:: " + str(xmin_a) + " LongMAX_A :: " + str(xmax_a) + "\n"
			print "LatMIN_A:: " + str(ymin_a) + " LatMAX_A :: " + str(ymax_a) + "\n"
			
		
		cur.execute("SELECT * FROM USER_POST WHERE USERID = %s AND STATUS = %s", (friendid, "matched"))
		result2 = cur.fetchall()
		con.commit()
		for row in result2:
			lat_b = row[4]
			lon_b = row[5]
			r_b = row[6]	#---km unit
			xmin_b = lon_b-r_b/(111.320*math.cos(lat_b/180*math.pi)) -0.01
			xmax_b = lon_b+r_b/(111.320*math.cos(lat_b/180*math.pi)) +0.01
			ymin_b = lat_b-r_b/110.574 -0.01
			ymax_b = lat_b+r_b/110.574 +0.01
			
			print "LongMIN_B:: " + str(xmin_b) + " LongMAX_B :: " + str(xmax_b) + "\n"
			print "LongMIN_B:: " + str(ymin_b) + " LatMAX_B :: " + str(ymax_b) + "\n"
		
		cat="%"+cat+"%"
		
		cur.execute("CREATE TABLE USERA_RE AS SELECT A.INDEX_COL FROM BUSINESS AS A INNER JOIN BUSINESS_ATTR AS B "+
			"ON A.ID = B.ID WHERE A.CATEGORY LIKE %s AND A.LATITUDE <= %s AND A.LATITUDE >= %s AND "+
			" A.LONGITUDE <= %s AND A.LONGITUDE >= %s AND B.PRICE_RANGE = %s ;"
			,( cat, ymax_a, ymin_a, xmax_a, xmin_a, price ))
		con.commit()

		#cur.execute("CREATE TABLE USERA_RE AS SELECT A.INDEX_COL FROM BUSINESS AS A INNER JOIN BUSINESS_ATTR AS B "+
		#	"ON A.ID = B.ID WHERE A.LATITUDE <= %s AND A.LATITUDE >= %s AND "+
		#	" A.LONGITUDE <= %s AND A.LONGITUDE >= %s AND B.PRICE_RANGE = %s;"
		#	,( ymax_a, ymin_a, xmax_a, xmin_a, price))


		cur.execute("CREATE TABLE USERB_RE AS SELECT A.INDEX_COL FROM BUSINESS AS A INNER JOIN BUSINESS_ATTR AS B "+
			"ON A.ID = B.ID WHERE A.CATEGORY LIKE %s AND A.LATITUDE <= %s AND A.LATITUDE >= %s AND "+
			" A.LONGITUDE <= %s AND A.LONGITUDE >= %s AND B.PRICE_RANGE = %s ;"
			,( cat, ymax_b, ymin_b, xmax_b, xmin_b, price ))
		con.commit()
		#cur.execute("CREATE TABLE USERB_RE AS SELECT A.INDEX_COL FROM BUSINESS AS A INNER JOIN BUSINESS_ATTR AS B "+
		#	"ON A.ID = B.ID WHERE A.LATITUDE <= %s AND A.LATITUDE >= %s AND"
		#	" A.LONGITUDE <= %s AND A.LONGITUDE >= %s AND B.PRICE_RANGE = %s;"
		#	,( ymax_b, ymin_b, xmax_b, xmin_b, price))


		#con.commit()
		cur.execute("SELECT C.INDEX_COL FROM USERA_RE AS C INNER JOIN USERB_RE AS D ON C.INDEX_COL = D.INDEX_COL")
		business_index = cur.fetchall() ## the list generated based on the join of both
		con.commit()

		cur.execute("SELECT INDEX_ROW FROM USER_INFO WHERE USERID = %s", (userid,))
		resultx = cur.fetchall()
		con.commit()
		for row in resultx:
			userA_index = row[0]
		
		cur.execute("SELECT INDEX_ROW FROM USER_INFO WHERE USERID = %s", (friendid,))
		resulty = cur.fetchall()
		con.commit()
		for row in resulty:
			userB_index = row[0]

		#2, pass index of two user and filtered list of business index to algorithm, expect to get list of index in return
		if len(str(business_index)) > 3:	
			################################ need to preprocess before pass on
			print "have recommendation after filter"
	
			A_index = userA_index
			B_index = userB_index
			List = []
			for row in business_index:
				List.append(row[0]-1)

			rec_list = match_pair(A_index-1, B_index-1, List, pred_rating)
			#print "rec_list" +"::" + str(A_index-1) +"\n"
			#print "rec_list" +"::" + str(B_index-1) +"\n"
			#print "rec_list" +"::" + str(pred_rating) +"\n"
			#print "rec_list" +"::" + str(rec_list) +"\n"
			################################# end of this case
		else:
			##########################################DEAL with situation that got 0 after filter:
			print "have no match after filter"
			cur.execute("DROP TABLE USERA_RE")
			cur.execute("DROP TABLE USERB_RE")
			con.commit()
					
			cur.execute("CREATE TABLE USERA_RE AS SELECT A.INDEX_COL FROM BUSINESS AS A INNER JOIN BUSINESS_ATTR AS B "+
				"ON A.ID = B.ID WHERE A.LATITUDE <= %s AND A.LATITUDE >= %s AND "+
				" A.LONGITUDE <= %s AND A.LONGITUDE >= %s;"
				,( ymax_a, ymin_a, xmax_a, xmin_a))
			con.commit()

			cur.execute("CREATE TABLE USERB_RE AS SELECT A.INDEX_COL FROM BUSINESS AS A INNER JOIN BUSINESS_ATTR AS B "+
				"ON A.ID = B.ID WHERE A.LATITUDE <= %s AND A.LATITUDE >= %s AND "+
				" A.LONGITUDE <= %s AND A.LONGITUDE >= %s;"
				,( ymax_b, ymin_b, xmax_b, xmin_b))
			con.commit()

			cur.execute("SELECT C.INDEX_COL FROM USERA_RE AS C INNER JOIN USERB_RE AS D ON C.INDEX_COL = D.INDEX_COL")
			business_index = cur.fetchall() ## the list generated based on the join of both
			con.commit()

			A_index = userA_index
			B_index = userB_index
			List = []
			for row in business_index:
				List.append(row[0]-1)

			rec_list = match_pair(A_index-1, B_index-1, List, pred_rating)
			#print "rec_list" +"::" + str(A_index-1) +"\n"
			#print "rec_list" +"::" + str(B_index-1) +"\n"
			#print "rec_list" +"::" + str(pred_rating) +"\n"
			#print "rec_list" +"::" + str(rec_list) +"\n"

			###########################################END of this modification
			
		#call the two algorithm function~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		#3, insert into database and expect user to check actively
		for each in rec_list:
			cur.execute("SELECT ID FROM BUSINESS WHERE INDEX_COL = %s ORDER BY STARS DESC LIMIT 10;", (each+1,))
			con.commit()
			#print str(each+1) +"\n"
			for row in cur.fetchall():
				index = row[0]  #get id for the index
				#print "index ::" + str(index) +"\n"
 
			cur.execute("INSERT INTO EVENT (USERID_A, USERID_B, BUSINESS_ID, MEET_TIME, MEET_DATE, STATUS) "
				+"VALUES (%s, %s, %s, %s, %s, %s)", (userid, friendid, index, start_time, datee, "SCHEDULED"))
			# will change to "ACCOMPLISHED after the date is passed"~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			con.commit()

		#4, delete from post table or change to another inactive state
		cur.execute("UPDATE USER_POST SET STATUS = %s WHERE USERID = %s AND STATUS = %s", ("done", userid, "matched"))
		cur.execute("UPDATE USER_POST SET STATUS = %s WHERE USERID = %s AND STATUS = %s", ("done", friendid, "matched"))
		con.commit()

		cur.execute("DROP TABLE USERA_RE")
		cur.execute("DROP TABLE USERB_RE")
		con.commit()

	except psycopg2.DatabaseError, e:
		if con:
			con.rollback()
    		print 'Error %s' % e    
    		sys.exit(1)
	finally:
    		if con:
       			 con.close()
	return

#function 8:-----------------------
#called after certain query on UI

def check_recommendation(userid):

	con=None
	friendid = None
	matched_person = {}
	recommend_restaurants = []

	try:
		con = psycopg2.connect("dbname='testdb' user='postgres'")   
		cur = con.cursor()

		#1, clear the event which start date as well as start hour has passed------------------------
		cur_date = datetime.datetime.now().strftime("%Y-%m-%d")
		cur_time = datetime.datetime.now().strftime("%H:%M:%S")

		cur.execute("UPDATE EVENT SET STATUS = %s WHERE MEET_TIME < %s AND MEET_DATE < %s AND STATUS = %s", 
			("ACCOMPLISHED", cur_time, cur_date, "SCHEDULED"))
		con.commit()
		
		#2, retrive the active info to user id
		cur.execute("SELECT A.NAME, A.ADDRESS, A.STARS, A.REVIEW_NUM, B.USERID_A, B.USERID_B FROM BUSINESS AS A INNER JOIN EVENT AS B ON "
			+"A.ID = B.BUSINESS_ID WHERE "
			+"(B.USERID_A = %s OR B.USERID_B = %s) AND B.STATUS = %s ORDER BY A.STARS DESC LIMIT 10", (userid, userid, "SCHEDULED"))
		result = cur.fetchall()
		con.commit()

		for row in result:
			newline = {"name": str(row[0]), "address": str(row[1]), "star": str(row[2])}
			recommend_restaurants.append(newline)
			if row[4] == userid:
				friendid = row[5]
			else:
				friendid = row[4]
				#print "Advised: " + str(row[0]) + " \n"
				
		#3, fetch friend info
		if friendid is not None:
			cur.execute("SELECT * FROM USER_INFO WHERE USERID = %s",(friendid,))
			result5 = cur.fetchall()
			matched_person = {"id": "", "name": "", "gender":"", "phone":"", "facebook":""};
			for row in result5:
				matched_person["id"] = row[0]
				matched_person["name"] = row[1]
				matched_person["gender"] = row[5]
				matched_person["phone"] = row[3]
				matched_person["facebook"] = row[8]
		else:
			pass # matched_person is empty

		con.commit()

	except psycopg2.DatabaseError, e:
		if con:
			con.rollback()
    		print 'Error %s' % e    
    		sys.exit(1)
	finally:
    		if con:
       			 con.close()

	return matched_person, recommend_restaurants



## Here is the test of all related functions:
#test function1
username1 = "33333333"
nickname1 = "L"
password = "123456"
phone = "1111111111"
gender = "female"
email1 = "2bilibilifwdq2@gmail.com"
facebook1 = "2bilibilifwdq2@facebook.com"
#token1 = add_user( username1, nickname1, password, phone, gender, email1,facebook1)
username2 = "44444444"
nickname2 = "Kira"
email2 = "2acfun_kilakil@gmail.com"
facebook2 = "2acfun_kilakil@facebook.com"
#token2 = add_user( username2, nickname2, password, phone, gender, email2,facebook2)
username3 = "55555555"
nickname3 = "Niya"
email3 = "2acfun_2333@gmail.com"
facebook3 = "2acfun_2333@facebook.com"
#token2 = add_user( username3, nickname3, password, phone, gender, email3,facebook3)

#print str(token1) + " " + str(token2)
#test function2
#token3 = check_user( email1, password)
#token4 = check_user( email2, password)
#print str(token3) + " " + str(token4)
#test function3
date = "2016-4-30"
latitude1 = "33.4171390787509" 
longitude1 = "-112.057581733744"
latitude2 = "33.4232672127535"
longitude2 =  "-112.074025075869"
#latitude1 = "33.4558849"
#longitude1 = "-112.0741767"
#latitude2 = "33.4157483" 
#longitude2 = "-112.0447870"
starthour = "10"
startmin = "30"
endhour = "16"
endmin = "30"
foodtype = "restaurant"
distance1 = "20"
distance2 = "20"
budget = "2"
gender = "female"
#token6 = add_proposal( username2, date, starthour, startmin, endhour, endmin, foodtype, distance2, budget, "female", latitude2, longitude2)
#token5 = add_proposal( username1, date, starthour, startmin, endhour, endmin, foodtype, distance1, budget, "female", latitude1, longitude1)

#token6 = add_proposal( username3, date, starthour, startmin, endhour, endmin, foodtype, distance2, budget, "female",latitude2, longitude2)
#test fucntion4
#accept_match(username1, username2)
#accept_match(username2, username1)
#accept_match(username1, username2)
#decline_match(username1, username2)

#pending1,token7 = check_match(username1)
#pending2,token8 = check_match(username2)
#print "check_match" + str(pending1) + " " +str(token7) +"\n"
#print "check_match" + str(pending2) + " " +str(token8) +"\n"

#pending3,token9 = check_match(username3)
#accept_match(username1, username2)
#accept_match(username2, username1)
#token6 = get_info_dashboard (username1)
#print str(token6)
#token7 = get_user_info (username2)
#print str(token7)

#token10, token11 = check_recommendation(username1)
#print "check_recom" + str(token10) + " " +str(token11) +"\n"
#token10, token11 = check_recommendation(username2)
#print "check_recom" + str(token10) +" "+ str(token11) +"\n"
#token10, token11 = check_recommendation(username3)
#print str(token10) +" "+ str(token11)
