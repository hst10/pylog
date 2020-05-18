from pylog import *
import random
import math
#import numpy as np


#Based on heterocl/samples/kmeans/kmeans_main.py
@pylog#(mode='pysim')
def pl_kmeans(points, means, labels):#, num_point, dim, num_cluster, num_iter):
    dim=32
    num_point=40
    num_cluster=5
    num_iter=10
    def dist(point, mean, tmp_array, dim):
        result = 0.0
        for idx in range(dim):
            tmp_array[idx]=point[idx]-mean[idx]
            result +=tmp_array[idx]**2
        return result

    def clear1D(cluster_num_element, num_cluster):
        for idx in range(num_cluster):
            cluster_num_element[idx]=0

    def clear2D(means,num_cluster,dim):
        for idx_cluster in range(num_cluster):
            for idx_dim in range(dim):
                means[idx_cluster,idx_dim]=0.0

    tmp_distance=np.zeros(dim,dtype=np.single)
    cluster_num_element=np.zeros(num_cluster,dtype=np.int32)

    for idx_iter in range(num_iter):
        #assign cluster
        for idx_point in range(num_point):
            label = -1
            min_dist = math.inf
            for idx_cluster in range(num_cluster):
                curr_dist = dist(points[idx_point],means[idx_cluster],tmp_distance,dim)
                if curr_dist<min_dist:
                    min_dist=curr_dist
                    label=idx_cluster
            labels[idx_point]=label

        #update mean
        clear1D(cluster_num_element,num_cluster)
        clear2D(means,num_cluster,dim)
        for idx_point in range(num_point):
            curr_label = labels[idx_point]
            cluster_num_element[curr_label]+=1
            for idx_dim in range(dim):
                means[curr_label,idx_dim]+=points[idx_point,idx_dim]
        for idx_cluster in range(num_cluster):
            for idx_dim in range(dim):
                means[idx_cluster,idx_dim]/=cluster_num_element[idx_cluster]
    return 0







if __name__=="__main__":
    dim=32
    num_point=40
    num_iter = 10
    num_cluster = 5
    points=np.random.rand(num_point,dim).astype(np.single)
    means=points[random.sample(range(num_point),num_cluster),:]
    labels = np.zeros(num_point,dtype=np.int32)
    pl_kmeans(points, means, labels)#, num_point,dim,num_cluster,num_iter)