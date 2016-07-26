import os
import urllib, hashlib
import shutil
import requests
import os.path
import numpy as np
from scipy.sparse import csr_matrix
from pprint import pprint
file_name = "matrix/rating_matrix.csv"
import matplotlib.pyplot as plt

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
    print "recomm_list: ", recomm_list        
    return recomm_list

if __name__ == "__main__":
    pred_rating = np.load("baseline_matrix.npy")
    a_index = 2
    b_index = 15
    rest_list = [0,10,20,33,500,30,2050,250,251]
    recomm_list = match_pair(a_index, b_index, rest_list, pred_rating)


