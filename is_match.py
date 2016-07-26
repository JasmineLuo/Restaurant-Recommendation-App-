import datetime as dt
import math


#def get_distance(lat1, lon1, lat2, lon2):
#    p = 0.017453292519943295
#    a = 0.5 - cos((lat2 - lat1) * p)/2 + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
#    return 12742 * asin(sqrt(a))

def get_distance(lat1, lon1, lat2, lon2):
    y = 110.574*abs(lat2-lat1)
    x = 111.320*math.cos(min(lat1,lat2)/180*math.pi)*abs(lon2-lon1)
    return math.sqrt(math.pow(x,2)+math.pow(y,2))

#check whether two users match based on information from posts
def is_match(post_a, post_b, gender_a, gender_b):
    #1. check time (index: 2 & 3)
    start_time_a = post_a[2]
    end_time_a = post_a[3]
    start_time_b = post_b[2]
    end_time_b = post_b[3]
    #print "start_time: ", post_a[2]
    t1 = max(start_time_a, start_time_b)
    t2 = min(end_time_a, end_time_b)
    #get overlap
    dt1 = dt.timedelta(hours=t1.hour, minutes=t1.minute, seconds=t1.second, microseconds=t1.microsecond)
    dt2 = dt.timedelta(hours=t2.hour, minutes=t2.minute, seconds=t2.second, microseconds=t2.microsecond)
    overlap = (dt2-dt1).total_seconds()
    #total seconds in 1 hour
    one_hour = 3600
    #overlap time less than 1 hour --> no match
    #print overlap
    if(overlap < one_hour):
	print "time failed\n"
        return False
    #2. check location (index: 4:lat,5:long,6:radius)
    distance = get_distance(post_a[4], post_b[5], post_b[4], post_b[5])
    total_radius = post_a[6] + post_b[6]
    if(total_radius < distance):
	print "distance failed\n"
        return False
    #3. check price (index: 7)
    if(post_a[7] != post_b[7]):
	print "price failed\n"
        return False
    #4. check gender (index: 8)
    if (post_a[8] != gender_b or post_b[8] != gender_a):
	print post_a[8] + gender_b + post_b[8] + gender_a +"\n"
	print "gender failed\n"
        return False
    #5. check food type (index: 9)
    if(post_a[9] != post_b[9]):
	print "type failed\n"
        return False
    #every criteria matched --> return true
    return True

