import json
import string
import psycopg2
import sys
import os
#import re
from pprint import pprint

business_filename='./yelp_academic_dataset_business.json'
script_dir = os.path.dirname(__file__)
rel_path = business_filename
abs_file_path = os.path.join(script_dir, rel_path)


def addtuple_business(jsonline,cur):
	# First: attribute: #######################################################
	attribute_all=jsonline["attributes"]
	# here deal with all attributes that I think is neccessary for database
	# attributes with multiple values are not included:
	# ambience, delivery, drive-thru, good_for (breakfast, lunch...), has_TV, Outdoor_Seating
	# NULL value "None" refers to no available value
	# For boolean values, Use False when result is not applicable
	# category is multi-value, it's hard to define the maximum how many item are needed, hence I just change 
	# them to strings, thus we can still search for keyword

	#1	
	if 'Accepts Credit Cards'in attribute_all.keys():
		Accept_Credit_Card = attribute_all['Accepts Credit Cards']
	else:
		Accept_Credit_Card = True
	#2
	if 'Alcohol'in attribute_all.keys():
		Alcohol = attribute_all['Alcohol']
		tok="none"
		if string.find(Alcohol,tok)!=-1: 
			Alcohol = False
		else:
			Alcohol = True
	else:
		Alcohol = True

	#3
	if 'Good for Kids'in attribute_all.keys():
		For_Kids = attribute_all['Good for Kids']
	else:
		For_Kids = True

	#4
	if 'Parking'in attribute_all.keys():
		park = ''.join('{}{}'.format(key, val) for key, val in  attribute_all['Parking'].items())
		ss = "True"
		# if "True" in any type of Parking, the result is true
		if string.find(park.lower(),ss.lower())!=-1: 
			Parking = True
		else:
			Parking = False
	else:
		Parking = True
	#5
	if 'Price Range'in attribute_all.keys():
		Price_Range = attribute_all['Price Range']
	else:
		Price_Range = None

	#7 8 9
	if 'Good For' in attribute_all.keys():

		if 'brunch' in attribute_all['Good For']:
			breakfast = attribute_all['Good For']['brunch']
			lunch = attribute_all['Good For']['brunch']
		else:
			breakfast = True
			lunch = True

		if 'breakfast' in attribute_all['Good For']:
			breakfast = attribute_all['Good For']['breakfast']
		else:
			breakfast = True

		if 'lunch' in attribute_all['Good For']:
			lunch = attribute_all['Good For']['lunch']
		else:
			lunch = True

		if 'dinner' in attribute_all['Good For']:
			dinner = attribute_all['Good For']['dinner']
		else:
			dinner = True

	else:	
		breakfast = True
		lunch = True
		dinner = True

	
	
	# Second: ID: ########PRIMARY KEY#########################
	ID=jsonline["business_id"]

	# 3rd: categories: #################################
	categories=str(jsonline["categories"]).lower()
	#categories = ''.join('{}{}'.format(key, val) for key, val in  jsonline["categories"])
	ss1 = "food"
	ss2 = "restaurant"
	ss3 = "bar"
	ss4 = "coffee"
		# if "True" in any type of Parking, the result is true
	if string.find(categories.lower(),ss1)!=-1 or string.find(categories.lower(),ss2)!=-1 or string.find(categories.lower(),ss3)!=-1 or string.find(categories.lower(),ss4)!=-1:
		cat = True
	else:
		cat = False
    # leave out the options that is not restaurant
	
	# 4th: city: #################################
	city=jsonline["city"]

	# 5th: full_address :##########################
	full_address=jsonline["full_address"]

	# 6th: latitude: ######################
	latitude = jsonline["latitude"]

	# 7th: longitude: ######################
	longitude = jsonline["longitude"] ###latitute and longitude are all integers

	# 8th: name: ######################
	name = jsonline["name"]
	
	# 9th: open: ######################
	open_state = jsonline["open"]

	# 10th: review_count: ######################
	review_count = jsonline["review_count"]

	# 11th: stars: ######################
	stars = jsonline["stars"]

	# 12th: state: ######################
	state = jsonline["state"]

	############### Service hours ###################
	hours = jsonline["hours"]
	if 'Monday'in hours.keys():
		Monday_open = hours["Monday"]["open"]  #---------need to convert to date form?
		Monday_close = hours["Monday"]["close"]
	else:
		Monday_open = None
		Monday_close = None
		
	if 'Tuesday'in hours.keys():
		Tuesday_open = hours["Tuesday"]["open"]  #---------need to convert to date form?
		Tuesday_close = hours["Tuesday"]["close"]
	else:
		Tuesday_open = None
		Tuesday_close = None	
	
	if 'Wednsday'in hours.keys():
		Wednsday_open = hours["Wednsday"]["open"]  #---------need to convert to date form?
		Wednsday_close = hours["Wednsday"]["close"]
	else:
		Wednsday_open = None
		Wednsday_close = None

	if 'Thursday'in hours.keys():
		Thursday_open = hours["Thursday"]["open"]  #---------need to convert to date form?
		Thursday_close = hours["Thursday"]["close"]
	else:
		Thursday_open = None
		Thursday_close = None

	if 'Friday'in hours.keys():
		Friday_open = hours["Friday"]["open"]  #---------need to convert to date form?
		Friday_close = hours["Friday"]["close"]
	else:
		Friday_open = None
		Friday_close = None

	if 'Saturday'in hours.keys():
		Saturday_open = hours["Saturday"]["open"]  #---------need to convert to date form?
		Saturday_close = hours["Saturday"]["close"]
	else:
		Saturday_open = None
		Saturday_close = None

	if 'Sunday'in hours.keys():
		Sunday_open = hours["Sunday"]["open"]  #---------need to convert to date form?
		Sunday_close = hours["Sunday"]["close"]
	else:
		Sunday_open = None
		Sunday_close = None

	# insert into database###################
        print str(open_state) +" "+ str("Phoenix" in city) + "\n"
	#table 1:
	if  (open_state) and ("Phoenix" in city) and cat:
            pprint ("business success added")
	    cur.execute("INSERT INTO BUSINESS VALUES( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",(ID, name, open_state,
			categories,city,full_address,latitude, longitude,stars,review_count,state ))
	#table 2:
	    cur.execute("INSERT INTO BUSINESS_ATTR VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",(ID,Accept_Credit_Card, Alcohol,
			For_Kids, Parking, Price_Range, breakfast, lunch, dinner))
	#table 2:
	    cur.execute("INSERT INTO BUSINESS_HOUR VALUES( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )", (
		    ID, Monday_open, Monday_close, Tuesday_open, Tuesday_close, Wednsday_open, Wednsday_close, Thursday_open,
		    Thursday_close, Friday_open, Friday_close, Saturday_open, Saturday_close, Sunday_open, Sunday_close,))
        
	else:
		pass
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
    cur.execute("DROP TABLE IF EXISTS BUSINESS_ATTR")
    cur.execute("DROP TABLE IF EXISTS BUSINESS_HOUR")
    cur.execute("DROP TABLE IF EXISTS BUSINESS")

    cur.execute("CREATE TABLE IF NOT EXISTS BUSINESS(ID VARCHAR(90) PRIMARY KEY, "+
		"NAME VARCHAR(100), OPEN BOOLEAN, CATEGORY VARCHAR(250), CITY VARCHAR(45), ADDRESS VARCHAR(250),"+
		"LATITUDE FLOAT, LONGITUDE FLOAT, STARS FLOAT, REVIEW_NUM INTEGER, STATE VARCHAR(8), INDEX_COL SERIAL)")
    
    cur.execute("CREATE TABLE IF NOT EXISTS BUSINESS_ATTR( ID VARCHAR(90) PRIMARY KEY REFERENCES BUSINESS(ID) ON DELETE CASCADE," +
		"CREDIT BOOLEAN, ALCOHOL BOOLEAN, KID BOOLEAN, PARKING BOOLEAN, PRICE_RANGE FLOAT, BREAKFAST BOOLEAN," +
		"LUNCH BOOLEAN, DINNER BOOLEAN)")

    cur.execute("CREATE TABLE IF NOT EXISTS BUSINESS_HOUR ( ID VARCHAR(90) PRIMARY KEY REFERENCES BUSINESS(ID) ON DELETE CASCADE,"+
		"MON_S time, MON_E time,"+
		"TUE_S time, TUE_E time,"+
		"WED_S time, WED_E time,"+
		"THU_S time, THU_E time,"+
		"FRI_S time, FRI_E time,"+
		"SAT_S time, SAT_E time,"+
		"SUN_S time, SUN_E time"+
		")")
    
    cur.execute("CREATE INDEX BUSINESS_CITY_INDEX ON BUSINESS (CITY);")
    cur.execute("CREATE INDEX BUSINESS_LAT_INDEX ON BUSINESS (LATITUDE);")
    cur.execute("CREATE INDEX BUSINESS_LOG_INDEX ON BUSINESS (LONGITUDE);")
    cur.execute("CREATE INDEX BUSINESS_CAT_INDEX ON BUSINESS (CATEGORY);")
    cur.execute("CREATE INDEX BUSINESS_PRICE_INDEX ON BUSINESS_ATTR (PRICE_RANGE);")
#import data line by line

    with open(abs_file_path) as f:
    		for line in f:
        		while True:
            			try:
                			jfile = json.loads(line)
                			#pprint(jfile)
                			#insert into database
					        #addtuple_business(jfile,cur)
					        
                			break
            			except ValueError:
                			# Not yet a complete JSON value
                			line += next(f)
                	##pprint(jfile)
			#insert into database
			addtuple_business(jfile,cur)
	#import into business table is done

	#find out the cities with more restaurant
    

    con.commit()
    
    #cur.execute("CREATE INDEX CONCURRENTLY BUSINESS_CITY_INDEX ON BUSINESS (CITY);")
    #cur.execute("CREATE INDEX CONCURRENTLY BUSINESS_LAT_INDEX ON BUSINESS (LATITUDE);")
    #cur.execute("CREATE INDEX CONCURRENTLY BUSINESS_LOG_INDEX ON BUSINESS (LONGITUDE);")
    #cur.execute("CREATE INDEX CONCURRENTLY BUSINESS_CAT_INDEX ON BUSINESS (CATEGORY);")
    #cur.execute("CREATE INDEX CONCURRENTLY BUSINESS_PRICE_INDEX ON BUSINESS_ATTR (PRICE_RANGE);")
    #the index is all locked for the table, since concurently option failed after several attemption, only normal index
    # ... are added

except psycopg2.DatabaseError, e:
	if con:
        	con.rollback()
    	print 'Error %s' % e    
    	sys.exit(1)
      
finally:
    
    if con:
        con.close()
#pprint(data)
