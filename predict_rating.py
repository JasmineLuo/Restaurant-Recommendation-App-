import os
import urllib, hashlib
import shutil
import requests
import os.path
import numpy as np
#from scipy.sparse import csr_matrix
from pprint import pprint
file_name = "matrix/rating_matrix.csv"
#import matplotlib.pyplot as plt

#load data
def load_data(file_name):
    rating_matrix = np.load(file_name)
    ratings = np.load("rows.npy")
    (num_user, num_bus) = rating_matrix.shape
    return (rating_matrix, ratings, num_user, num_bus)


def fill_rating_matrix(A_in, lambda2, lambda3, num_user,num_bus):
        #data set a, count number of ratings per movie
    A = A_in
    bus_ratings = (A != 0).sum(0)
    user_ratings = (A != 0).sum(1)
    mu_a = (A.sum())/(A != 0).sum()
    bi_a = np.zeros(shape = (num_bus,))

    masked_a = np.ma.masked_equal(A,0)
    bi_a = ((masked_a - mu_a).sum(0))/(lambda2 + bus_ratings)
    bi_a.mask = np.ma.nomask
    bu_a = np.zeros(shape = (num_user,))
    bu_a = ((masked_a - mu_a - bi_a).sum(1))/(lambda3 + user_ratings)
    bu_a.mask = np.ma.nomask
    bu_a = bu_a.reshape(bu_a.shape+(1,))

    bui_a = np.zeros(shape = (num_user,num_bus))
    x = [1,2,3]
    bi_a_matrix = np.tile(bi_a, (num_user, 1))
    bu_a_matrix = np.tile(bu_a,(1,num_bus))
    diff = 0;
    count = 0;
    count_none = 0;
    Rui = []
    for u in range(num_user):
        for i in range(num_bus):
            if(A[u][i] == 0):
                A[u][i] = mu_a + bu_a_matrix[u][i] + bi_a_matrix[u][i] #make prediction using mu, bu, and bi
     #           print "A[u][i]: ", A[u][i]

    return A

if __name__ == "__main__":
    (rating_matrix, ratings, num_user, num_bus) = load_data("rating_matrix.npy")
    pred_rating = fill_rating_matrix(rating_matrix, 25, 10, num_user,num_bus)
    np.save("baseline_matrix.npy",pred_rating)

