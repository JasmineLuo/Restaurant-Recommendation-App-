import json
import string
import psycopg2
import sys
import os
from pprint import pprint

business_filename='./yelp_academic_dataset_review.json'
script_dir = os.path.dirname(__file__)
rel_path = business_filename
abs_file_path = os.path.join(script_dir, rel_path)

def addtuple_review(jsonline,cur):
	#in this table, the date is only for display hence it is of string type

	#primary key
	comID=jsonline["review_id"]	
	# 1: ID: ########PRIMARY KEY#########################
	ID=jsonline["business_id"]

	# 2: name: #################################
	uID=jsonline["user_id"]
	
	# 3th: avestar: #################################
	date = ''.join(jsonline["date"])
	year = date.split('-')[0]
	month = date.split('-')[1]
	day = date.split('-')[2]
	#''.join(jfile["date"])

	# 4th: fans :##########################
	stars=jsonline["stars"]

	# insert into database###################
	#table 1:
	
	cur.execute("INSERT INTO USER_REVIEW_PRE VALUES( %s, %s, %s, %s, %s)",( comID, uID, ID, date, stars ))

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
#create table and all the rest table
    cur.execute("DROP TABLE IF EXISTS USER_REVIEW")
    cur.execute("DROP TABLE IF EXISTS USER_REVIEW_PRE")
#    cur.execute("DROP TABLE IF EXISTS USER_POST")
#    cur.execute("DROP TABLE IF EXISTS EVENT")
    

    cur.execute("CREATE TABLE IF NOT EXISTS USER_REVIEW_PRE ( COMID VARCHAR(45) PRIMARY KEY,"+
		"USERID VARCHAR(45),"+
		"ID VARCHAR(90), REVIEW_DATE DATE, "+
		"STARS FLOAT)") ## no reference business ID here, since not all are put into database
 
    #cur.execute("CREATE TABLE IF NOT EXISTS USER_POST ( POSTID VARCHAR(45) PRIMARY KEY ,USERID VARCHAR(45) NOT NULL,"+
#		"REFERENCES USER_INFO(USERID) ON DELETE CASCADE, START_TIME TIME, END_TIME TIME,"+
#		"LATITUDE FLOAT, LONGITUDE FLOAT,"+
#		"RADIUS FLOAT, PRICE FLOAT, GENDER VARCHAR(10), TYPE VARCHAR(120), DATEE DATE,"+
#		"STATUS VARCHAR(15) )")
	
#    cur.execute("CREATE TABLE IF NOT EXISTS EVENT (EVENT_ID VARCHAR(45) PRIMARY KEY, USERID_A VARCHAR(45)"+
#		"REFERENCES USER_INFO(USERID) ON DELETE CASCADE,"+
#		"USERID_B VARCHAR(45) REFERENCES USER_INFO(USERID) ON DELETE CASCADE,"+
#		"BUSINESS_ID VARCHAR(90) REFERENCES BUSINESS(ID) ON DELETE CASCADE,"+
#		"MEET_TIME TIME, MEET_DATE DATE, STATUS VARCHAR(15))")

#import data line by line
    with open(abs_file_path) as f:
    		for line in f:
        		while True:
            			try:
                			jfile = json.loads(line)
                			#pprint(jfile)
                			#insert into database
					#addtuple_business(jfile,cur)
					print("review success added")
                			break
            			except ValueError:
                			# Not yet a complete JSON value
                			line += next(f)
                	##pprint(jfile)
			#insert into database
			addtuple_review(jfile,cur)

	#generate the userreview that have been to certain city
    cur.execute("CREATE TABLE USER_REVIEW AS SELECT COMID, USERID, USER_REVIEW_PRE.ID, REVIEW_DATE, USER_REVIEW_PRE.STARS FROM "
                +"USER_REVIEW_PRE INNER JOIN BUSINESS ON USER_REVIEW_PRE.ID = BUSINESS.ID;")
    cur.execute("DROP TABLE USER_REVIEW_PRE;")
    print "USER_REVIEW table created and filled!"
    con.commit()

except psycopg2.DatabaseError, e:
	if con:
        	con.rollback()
    	print 'Error %s' % e    
    	sys.exit(1)
      
finally:
    
    if con:
        con.close()
#pprint(data)CREATE TABLE 
