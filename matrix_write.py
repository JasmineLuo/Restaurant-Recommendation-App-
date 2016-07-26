import json
import string
import psycopg2
import sys
import os
import urllib, hashlib
import shutil
import requests
import os.path
import numpy
from pprint import pprint

### one row refers to one user, one column refers to one business

script_dir = os.path.dirname(__file__)
rel_path = "matrix/rating_matrix.csv"
con=None

try:
     
    con = psycopg2.connect("dbname='testdb' user= 'postgres'")   
    cur = con.cursor()
   	
    # decide the size of matrix
    cur.execute("SELECT COUNT(*) FROM USER_INFO")
    ROW = cur.fetchone()[0]
    print ROW
 
    cur.execute("SELECT COUNT(*) FROM BUSINESS")
    COL = cur.fetchone()[0]
    print COL

    cur.execute("SELECT INDEX_ROW, INDEX_COL, USER_REVIEW.STARS, AVE_STAR, USER_INFO.REVIEW_NUM, BUSINESS.REVIEW_NUM "
        +"FROM (USER_INFO INNER JOIN USER_REVIEW "+
        "ON USER_INFO.USERID = USER_REVIEW.USERID) JOIN BUSINESS ON USER_REVIEW.ID = BUSINESS.ID")
    rows = cur.fetchall()
   # print "rows: ", rows
    #numpy.save("rows.npy", rows)
    # matrix initialization
    M = numpy.zeros(shape=(ROW,COL))
    count = 0;
    row_no_repeat = []
    for row in rows:
    # each in the form: row index, column index, stars, (avestars, review_num)
    # remember to -1 since it starts from 0 in array
	if(M[row[0]-1][row[1]-1] == 0):
		#print "new: ", row[2]
	#	print "old: ", M[row[0]-1][row[1]-1]
	#	print " " 
        	M[row[0]-1][row[1]-1] = row[2]
		count = count + 1
		row_no_repeat.append(row)
	#if (row[2] == 0.0):
	   # print "########rating of 0!!!"
        #print "filling... \n"
    print "count: ", count
    print "matrix complete! \n"
    numpy.save("rows.npy", row_no_repeat)
    con.commit()
    numpy.save("rating_matrix.npy",M)
    print "M len: ", len(M[M != 0])
    numpy.savetxt(rel_path, M, delimiter=",")
    print "matrix exported as csv"

    test = numpy.genfromtxt (rel_path, delimiter=",")
    print test.max()

except psycopg2.DatabaseError, e:
	if con:
        	con.rollback()
    	print 'Error %s' % e    
    	sys.exit(1)
      
finally:
    
    if con:
        con.close()		
