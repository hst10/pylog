from pylog import *
import random
import math
#import numpy as np


#Based on heterocl/samples/kmeans/kmeans_main.py
#@pylog(mode='deploytiming',board='zedboard')
@pylog(mode='hwgen',board='zedboard')
def pl_kmeans(points, means, labels, tmp_distance, cluster_num_element):#, num_point, dim, num_cluster, num_iter):
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
        pragma("HLS unroll factor=5")
        for idx in range(num_cluster):#TODO: replace hard coded with variable num_cluster
            cluster_num_element[idx]=0
        return 0 #TODO: compiler signature return type void if no return

    def clear1D_float(tmp_distance, dim):
        for idx in range(dim):
            tmp_distance[idx]=0.0
        return 0 #TODO: compiler signature return type void if no return

    def clear2D(means,num_cluster,dim):
        pragma("HLS unroll factor=5")
        for idx_cluster in range(num_cluster):#TODO: replace hard coded with variable num_cluster
            for idx_dim in range(dim):
                means[idx_cluster,idx_dim]=0.0
        return 0 #TODO: compiler signature return type void if no return



    for idx_iter in range(num_iter):
        #assign cluster

        for idx_point in range(num_point).pipeline():
            label = -1
            min_dist = 3.402823466e+38#TODO:Support math.inf
            for idx_cluster in range(num_cluster):
                #curr_dist = dist(points[idx_point,:],means[idx_cluster,:],tmp_distance,dim)#TODO: remove the redundant ",:"
                #TODO: use dist instead
                curr_dist = 0.0
                for idx in range(dim):
                    tmp_distance[idx] = points[idx_point,idx] - means[idx_cluster,idx]
                    curr_dist += tmp_distance[idx] * tmp_distance[idx]#TODO: support **2
                #TODO: use dist instead end
                if curr_dist<min_dist:
                    min_dist=curr_dist
                    label=idx_cluster
            labels[idx_point]=label

        #update mean
        clear1D(cluster_num_element,num_cluster)
        clear2D(means,num_cluster,dim)
        for idx_point in range(num_point).pipeline():
            curr_label = labels[idx_point]
            cluster_num_element[curr_label]+=1
            for idx_dim in range(dim):
                means[curr_label,idx_dim]+=points[idx_point,idx_dim]
        for idx_cluster in range(num_cluster).pipeline():
            for idx_dim in range(dim):
                means[idx_cluster,idx_dim]/=cluster_num_element[idx_cluster]
    return 0


#@pylog(mode='deploy',board='zedboard')
#def pl_kmeans(points, means, labels, tmp_distance, cluster_num_element)
#    return pl_kmeans_golden(points, means, labels, tmp_distance, cluster_num_element)




if __name__=="__main__":
    dim=32
    num_point=40
    num_iter = 10
    num_cluster = 5
    points=np.random.rand(num_point,dim).astype(np.single)
    means=points[random.sample(range(num_point),num_cluster),:]
    #labels = np.zeros(num_point,dtype=np.int32)#TODO: use np.zeros instead
    labels = np.empty(num_point, dtype=np.int32)

    np.save(os.path.join("tests","golden_reference","kmeans_points_init"),points)
    np.save(os.path.join("tests","golden_reference","kmeans_means_init"),means)
    np.save(os.path.join("tests","golden_reference","kmeans_labels_init"),labels)
    # tmp_distance=np.zeros(dim,dtype=np.single)#TODO: use np.zeros instead
    # cluster_num_element=np.zeros(num_cluster,dtype=np.int32)#TODO: use np.zeros instead
    tmp_distance = np.empty(dim, dtype=np.float)  # TODO: use np.single instead
    cluster_num_element = np.empty(num_cluster, dtype=np.int32)
    pl_kmeans(points, means, labels, tmp_distance, cluster_num_element)#, num_point,dim,num_cluster,num_iter)
    np.save(os.path.join("tests","golden_reference","kmeans_points"),points)
    np.save(os.path.join("tests","golden_reference","kmeans_means"),means)
    np.save(os.path.join("tests","golden_reference","kmeans_labels"),labels)
