from env import *
from pylog import *
import numpy as np

# Based on polybench2.0/image-processing/gauss-filter/gauss-filter.c
# N = 1080
# M = 1920
# T = 1920
# reduce size to fit in FPGA
N = 108
M = 192
T = 192


# @pylog(mode='deploytiming',board='zedboard')
@pylog(mode='hwgen', board='zedboard')
def pl_gauss_filter_5(in_image, Gauss, gauss_image):
    def compute(in_image, Gauss, tot, g_acc1, g_acc2, g_tmp_image, gauss_image):
        t = 192
        m = 192
        n = 108
        tot[0] = 0
        for k in range(t - 1, t + 2):
            tot[k + 2 - t] = tot[k + 1 - t] + Gauss[k - t + 1]
        for k in range(t - 1, t + 2):  # duplicate in original code
            tot[k + 2 - t] = tot[k + 1 - t] + Gauss[k - t + 1]

        for k in range(t - 1, t + 2):
            for x in range(1, n - 2).pipeline():
                for y in range(0, m).unroll():
                    g_acc1[x, y, 0] = 0
                    g_acc1[x, y, k + 2 - t] = g_acc1[x, y, k + 1 - t] + in_image[x + k - t, y] * Gauss[k - t + 1]
                    g_tmp_image[x, y] = g_acc1[x, y, 3] / tot[3]

        for k in range(t - 1, t + 2):
            for x in range(1, n - 1).pipeline():
                for y in range(1, m - 1).unroll():
                    g_acc2[x, y, 0] = 0
                    g_acc2[x, y, k + 2 - t] = g_acc2[x, y, k + 1 - t] + g_tmp_image[x, y + k - t] * Gauss[k - t + 1]
                    gauss_image[x, y] = g_acc2[x, y, 3] / tot[3]

    Gauss_buffer = np.empty((4,), float)
    in_image_buffer = np.empty((108, 192), float)
    gauss_image_buffer = np.empty((108, 192), float)

    pragma("HLS array_partition variable=Gauss_buffer complete")
    pragma("HLS array_partition variable=in_image_buffer block factor= dim=2")
    pragma("HLS array_partition variable=gauss_image_buffer block factor= dim=2")

    for i in range(4).unroll():
        Gauss_buffer[i] = Gauss[i]

    for i in range(108).pipeline():
        for j in range(192):
            in_image_buffer[i][j] = in_image[i][j]
            gauss_image_buffer[i][j] = gauss_image[i][j]

    tot = np.empty((4,), float)
    g_tmp_image = np.empty((108, 192), float)
    g_acc1 = np.empty((108, 192, 4), float)
    g_acc2 = np.empty((108, 192, 4), float)

    compute(in_image_buffer, Gauss_buffer, tot, g_acc1, g_acc2, g_tmp_image, gauss_image_buffer)

    for i in range(108).pipeline():
        for j in range(192):
            gauss_image_buffer[i][j] = gauss_image[i][j]


if __name__ == "__main__":
    def init_array(in_image, Gauss):
        for i in range(108):  # TODO: replace hard coded with N
            for j in range(192):  # TODO: replace hard coded with M
                in_image[i, j] = (i * j + 0.0) / 192  # TODO: replace hard coded with M
        for i in range(4):
            Gauss[i] = i
        return 0


    Gauss = np.zeros(4, dtype=np.float)
    in_image = np.zeros((108, 192), dtype=np.float)
    init_array(in_image, Gauss)
    gauss_image = np.zeros((108, 192), dtype=np.float)

    start = time.time()
    pl_gauss_filter_5(in_image, Gauss, gauss_image)
    total_time = (time.time() - start)

    print("Average kernel time (s): {:.10f}".format(total_time))
'''
    pl_gauss_filter(in_image, Gauss, tot, g_acc1, g_acc2, g_tmp_image, gauss_image)
    np.save(os.path.join("tests","golden_reference","gauss_filter_in_image"),in_image)
    np.save(os.path.join("tests","golden_reference","gauss_filter_Gauss"),Gauss)
    np.save(os.path.join("tests","golden_reference","gauss_filter_gauss_image"),gauss_image)
    np.save(os.path.join("tests","golden_reference","gauss_filter_g_acc1"),g_acc1)
    np.save(os.path.join("tests","golden_reference","gauss_filter_g_acc2"),g_acc2)
    np.save(os.path.join("tests","golden_reference","gauss_filter_tot"),tot)
    np.save(os.path.join("tests","golden_reference","gauss_filter_g_tmp_image"),g_tmp_image)
    '''
