##CAUTION: calling this function will overwrite "baseline_matrix.npy"
import numpy as np

def append_predict_matrix():
    current_matrix = np.load("baseline_matrix.npy")
    (num_user, num_bus) = current_matrix.shape
    itemized_ratings = np.load("rows.npy")
    new_user = np.zeros((1,num_bus))
    
    for i in range(len(itemized_ratings)):
        bus_index = itemized_ratings[i,1]
        #if (new_user[bus_index-1] == 0):
        new_user[0,bus_index-1] = itemized_ratings[i,4]
        ##print "bus_index: ", bus_index
        #print "rating: ", new_user[0,bus_index-1]
   # print new_user
    new_matrix = np.concatenate((current_matrix, new_user), axis=0)
    #print new_matrix
    np.save("baseline_matrix.npy",new_matrix)
