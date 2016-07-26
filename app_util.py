#!/usr/bin/env python

from flask import request
import psycopg2

def cookie_check():
    """
    Check the cookie info of client
    If the cookie is authenticated then return True
    If the cookie is not correct then return False
    If no cookie found then return None
    """

    username = request.cookies.get("username")
    print "USERNAME IN COOKIE:: "+ str(username) +"\n"
    password = request.cookies.get("password")  # only the SHA1 digest
    print "PASWORD IN COOKIE:: "+ str(password) +"\n"
    # TODO: query for the username and password in the database

    if (username is None) or (password is None):
        print "COOKIE NOT YET SETTED"
        return None

    con = None
    try:

        try:
     
	    con = psycopg2.connect("dbname='testdb' user='postgres'")   
	    cur = con.cursor()
	    cur.execute('SELECT * FROM USER_INFO WHERE USERID = %s AND PASSWORD = %s;',(username, password))
	    result = cur.fetchall()

	    con.commit()

        except psycopg2.DatabaseError, e:
            if con:
        	    con.rollback()
    	    print 'Error %s' % e    
    	    sys.exit(1)
      
        finally:
    
           if con:
               con.close()

        if len(str(result))<=3:
            match = False  # placeholder
            return match
        else:
            match = True
            return match
        
    except KeyError:
            # No cookie found
        return None
