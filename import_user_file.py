import json
import string
import psycopg2
import sys
import os
from pprint import pprint
from random import randint

business_filename='./yelp_academic_dataset_user.json'
script_dir = os.path.dirname(__file__)
rel_path = business_filename
abs_file_path = os.path.join(script_dir, rel_path)
COUNT=0

def addtuple_user(jsonline,cur):
	# First: attribute: #######################################################
	friends_all=jsonline["friends"]
	# here deal with all attributes that I think is neccessary for database
	# attributes with multiple values are not included:
	# ambience, delivery, drive-thru, good_for (breakfast, lunch...), has_TV, Outdoor_Seating
	# NULL value "None" refers to no available value
	# For boolean values, Use False when result is not applicable
	# category is multi-value, it's hard to define the maximum how many item are needed, hence I just change 
	# them to strings, thus we can still search for keyword

	# 1: ID: ########PRIMARY KEY#########################
	ID=jsonline["user_id"]

	# 2: name: #################################
	uname=jsonline["name"]
	
	# 3: pw
	password = "123456" ## default for yelp user

	# 4: phone
	phone = "0123456789" ## default for yelp user

	# 5: email
	email = ID+"@gmail.com"  ## default for yelp user

	# 6: gender
	if(randint(0,1)==0):
		gender="male"
	else:
		gender="female"  ## default for yelp user

	# 7th: avestar: #################################
	avestar=jsonline["average_stars"]

	# 8th: review_count: ######################
	review_count = jsonline["review_count"]

	# 9th: facebook
	facebook = "https://www.facebook.com/" + ID  ##default for yelp user
	

	# insert into database###################
    
    # find whether in this list:
        cur.execute("SELECT USERID FROM TEMP WHERE TEMP.USERID = %s;", (ID,))
        result3=cur.fetchone()
	print str(result3)
	#table 1:
        if result3 is not None:
	        cur.execute("INSERT INTO USER_INFO VALUES( %s, %s, %s, %s, %s, %s, %s, %s, %s);",(ID, uname, password, 
		        phone, email, gender, avestar, review_count, facebook ))
                print "user added!"
		#COUNT = COUNT+1
	#table 2:
	        #for friend in friends_all:
                 #   result4 = cur.execute("SELECT * FROM TEMP WHERE USERID = %s;", (friend,))
                  #  if result4 is not None:
		   #             cur.execute("INSERT INTO USER_CONNECTION VALUES(%s,%s,%s);",(ID,friend,"DONE",None))
                    #else:
                     #   pass
        else:
            print "user ignored"

	return
# function end

# process business data main function
###~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
###~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#databse connection
con=None

try:
     
    con = psycopg2.connect("dbname='testdb' user='postgres'")   
    cur = con.cursor()
#create table
    cur.execute("DROP TABLE IF EXISTS USER_CONNECTION")
    cur.execute("DROP TABLE IF EXISTS USER_INFO")

    cur.execute("CREATE TABLE IF NOT EXISTS USER_INFO ( USERID VARCHAR(45) PRIMARY KEY, USERNAME VARCHAR(90), "+
		"PASSWORD VARCHAR(20), PHONE VARCHAR(15), EMAIL VARCHAR(45), GENDER VARCHAR(10), AVE_STAR FLOAT,"+
		"REVIEW_NUM INTEGER, FACE_BOOK_LINK VARCHAR(120), INDEX_ROW SERIAL)")
    
    cur.execute("CREATE TABLE IF NOT EXISTS USER_CONNECTION ( CON_ID SERIAL PRIMARY KEY, USERID VARCHAR(45) NOT NULL "
    +"REFERENCES USER_INFO(USERID) ON DELETE CASCADE, FRIENDID VARCHAR(45) NOT NULL, STATUS VARCHAR(15), TIMER TIME)") 

    # temp table    
    cur.execute("CREATE TABLE TEMP AS SELECT USER_REVIEW.USERID FROM USER_REVIEW GROUP BY USERID ORDER BY COUNT(*) DESC LIMIT 1000;")
    #cur.execute("SELECT ID FROM TEMP;")
    #result5 = cur.fetchall()
    #count = 0
    #for line in result5:
    #    print str(line) + " " +str(count)
    #    count = count+1

    # least review number is around 42
	# temp list for 

#import data line by line
    with open(abs_file_path) as f:
    		for line in f:
        		while True:
            			try:
                			jfile = json.loads(line)
                			break
            			except ValueError:
                			# Not yet a complete JSON value
                			line += next(f)
			addtuple_user(jfile,cur)
	#import into business table is done
    cur.execute("DROP TABLE TEMP;")
    con.commit()

except psycopg2.DatabaseError, e:
	if con:
        	con.rollback()
    	print 'Error %s' % e    
    	sys.exit(1)
      
finally:
    
    if con:
        con.close()
#pprint(data)
