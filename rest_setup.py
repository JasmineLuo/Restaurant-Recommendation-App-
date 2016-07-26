import json
import string
import psycopg2
import sys
import os
import urllib, hashlib
import shutil
import requests
import os.path
from predict_rating import *
from pprint import pprint

### fist fillup matrix
(rating_matrix, ratings, num_user, num_bus) = load_data("rating_matrix.npy")
pred_rating = fill_rating_matrix(rating_matrix, 25, 10, num_user,num_bus)
np.save("baseline_matrix.npy",pred_rating)

### second generate  default image for all these users
# use Gravator

#script_dir = os.path.dirname(__file__)
#default = "http://www.example.com/default.jpg"
#size = 40
con=None

try:
     
    con = psycopg2.connect("dbname='testdb' user='postgres'")   
    cur = con.cursor()
   
    # Part 1 set up two table
    cur.execute("DROP TABLE IF EXISTS USER_POST")
    cur.execute("DROP TABLE IF EXISTS EVENT")

    cur.execute("CREATE TABLE IF NOT EXISTS USER_POST ( POSTID VARCHAR(45) PRIMARY KEY ,USERID VARCHAR(45) NOT NULL "+
		"REFERENCES USER_INFO(USERID) ON DELETE CASCADE, START_TIME TIME, END_TIME TIME,"+
		"LATITUDE FLOAT, LONGITUDE FLOAT,"+
		"RADIUS FLOAT, PRICE FLOAT, GENDER VARCHAR(10), TYPE VARCHAR(120), DATEE DATE,"+
		"STATUS VARCHAR(15) )")
	
    cur.execute("CREATE TABLE IF NOT EXISTS EVENT (EVENT_ID SERIAL PRIMARY KEY, USERID_A VARCHAR(45)"+
		"REFERENCES USER_INFO(USERID) ON DELETE CASCADE,"+
		"USERID_B VARCHAR(45) REFERENCES USER_INFO(USERID) ON DELETE CASCADE,"+
		"BUSINESS_ID VARCHAR(90) REFERENCES BUSINESS(ID) ON DELETE CASCADE,"+
		"MEET_TIME TIME, MEET_DATE DATE, STATUS VARCHAR(15))")

    # Part 2 gengerate avatar
    #cur.execute("SELECT USERID, EMAIL FROM USER_INFO")
    #rows = cur.fetchall()

    #for row in rows:
	# execute image request http://en.gravatar.com/site/implement/
	# construct url

	#rel_path = "user_image/"+row[0]+".png"

	#if os.path.exists(rel_path):
		# pass if the image already obtained
	#	print 'ignored: ' + rel_path
	#else:
	#	email= "cse6242D5"+row[1]
	#	gravatar_url = "http://www.gravatar.com/avatar/" + hashlib.md5(email.lower()).hexdigest() + "?"
	#	gravatar_url += urllib.urlencode({'d': "identicon",'s':str(size)})
		# get image
		#response = requests.get(gravatar_url, stream=True)
	#	print 'got: ' + email

		#abs_file_path = os.path.join(script_dir, rel_path)
		#pprint(abs_file_path)
	#	urllib.urlretrieve(gravatar_url, rel_path)

    con.commit()

except psycopg2.DatabaseError, e:
	if con:
        	con.rollback()
    	print 'Error %s' % e    
    	sys.exit(1)
      
finally:
    
    if con:
        con.close()		
