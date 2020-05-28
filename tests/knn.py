from env import *
import numpy as np
from pylog import *
from digitrec_data import read_digitrec_data
import time

@pylog(mode='hwgen', board='zedboard', freq=25.0)
def knn(train_images_in,test_image_in,knn_mat_in ):

    train_images = np.empty((10,1800), pl_fixed(64, 64))
    knn_mat = np.empty((10,3), pl_fixed(64, 64))

    pragma("HLS array_partition variable=train_images complete")
    pragma("HLS array_partition variable=knn_mat complete")

    #create buffers
    for y in range(1800).pipeline():
       # for x in range(10).unroll():
        train_images[0][y] = train_images_in[0][y]
        train_images[1][y] = train_images_in[1][y]
        train_images[2][y] = train_images_in[2][y]
        train_images[3][y] = train_images_in[3][y]
        train_images[4][y] = train_images_in[4][y]
        train_images[5][y] = train_images_in[5][y]
        train_images[6][y] = train_images_in[6][y]
        train_images[7][y] = train_images_in[7][y]
        train_images[8][y] = train_images_in[8][y]
        train_images[9][y] = train_images_in[9][y]


    test_image = test_image_in[0]
    for x in range(10).pipeline():
        for y in range(3).unroll():
            knn_mat[x][y] = knn_mat_in[x][y]


    for y in range(1800).pipeline():
        for x in range(10).unroll(10):
            diff = test_image ^ train_images[x][y]
            one = 1
            dist = 1
            for i in range(49).unroll(49):
                dist = dist + ((diff>>i)&one)
            max_id = 0
            max_v = 0
            for i in range(3).unroll(3):
                if (knn_mat[x][i]> max_v):
                    max_v = knn_mat[x][i]
                    max_id = i
            if (dist<max_v):
                knn_mat[x][max_id] = dist

    for x in range(10).unroll():
        for y in range(3).unroll():
            knn_mat_in[x][y] = knn_mat[x][y]

if __name__ == "__main__":
    def knn_vote(knn_mat):
        knn_mat.sort(axis = 1)
        knn_score = np.zeros(10)

        for i in range(0, 3):
            min_id = np.argmin(knn_mat, axis = 0)[i]
            knn_score[min_id] += 1

        return np.argmax(knn_score)

    # Data preparation
    train_images, _, test_images, test_labels = read_digitrec_data()

    # Classification and testing
    correct = 0.0

    # We have 180 test images
    total_time = 0
    test_image = np.zeros((2,),dtype=np.int64)

    for i in range(0, 1):

        # Prepare input data to offload function
       # pylog_knn_mat = np.empty((10,3), pl_fixed(6, 6)) + 50
        pylog_knn_mat = np.zeros((10,3),dtype=np.int64) +50
        test_image[0] = test_images[i]

        # Execute the offload function and collect the candidates
        start = time.time()
        knn(train_images,test_image,pylog_knn_mat)
        total_time = total_time + (time.time() - start)

        # Feed the candidates to the voting algorithm and compare the labels
        if knn_vote(pylog_knn_mat) == test_labels[i]:
            correct += 1
        #total_time = total_time + (time.time() - start)


    print("Average kernel time (s): {:.10f}".format(total_time/180))
    print("Accuracy (%): {:.10f}".format(100*correct/180))



