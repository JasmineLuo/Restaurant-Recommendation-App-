import json
import string
import psycopg2
import sys
from pprint import pprint

con=None

try:
     
	con = psycopg2.connect("dbname='testdb' user='postgres'")   
	cur = con.cursor()
    #cur.execute("CREATE TABLE USER_REVIEW AS SELECT COMID, USERID, USER_REVIEW_PRE.ID, REVIEW_DATE, STARS FROM "
     #           +"USER_REVIEW_PRE INNER JOIN BUSINESS ON USER_REVIEW_PRE.ID = BUSINESS.ID;")
    #cur.execute("DROP TABLE USER_REVIEW_PRE;")
    #print "USER_REVIEW table created and filled!"
    #cur.execute('SELECT * FROM USER_REVIEW')
    #cur.execute("SELECT USERID, COUNT(*) FROM USER_REVIEW GROUP BY USERID ORDER BY COUNT(*) DESC LIMIT 1000;")
	#cur.execute("DROP TABLE EVENT")
	#cur.execute("CREATE TABLE IF NOT EXISTS EVENT (EVENT_ID SERIAL PRIMARY KEY, USERID_A VARCHAR(45)"+
	#	"REFERENCES USER_INFO(USERID) ON DELETE CASCADE,"+
	#	"USERID_B VARCHAR(45) REFERENCES USER_INFO(USERID) ON DELETE CASCADE,"+
	#	"BUSINESS_ID VARCHAR(90) REFERENCES BUSINESS(ID) ON DELETE CASCADE,"+
	#	"MEET_TIME TIME, MEET_DATE DATE, STATUS VARCHAR(15))")
	#cur.execute("DROP TABLE USERA_RE")
	#cur.execute("DROP TABLE USERB_RE")
	cur.execute("TRUNCATE TABLE EVENT")
	cur.execute("TRUNCATE TABLE USER_CONNECTION")
	cur.execute("TRUNCATE TABLE USER_POST")
	cur.execute('SELECT * FROM USER_POST')
	#current_time = time.strftime("%H:%M:%S")
	#result = cur.fetchall()
	#print str([result[0][0],result[1][0]])
	row_count = 0
	for row in cur:
		row_count += 1
		print "row: %s    %s\n" % (row_count, row)
	con.commit()

except psycopg2.DatabaseError, e:
	if con:
        	con.rollback()
    	print 'Error %s' % e    
    	sys.exit(1)
      
finally:
    
    if con:
        con.close()
