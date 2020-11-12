#include "dcl.h"
#include <math.h>
#include <fstream>
#include <hls_math.h>
#include <ap_fixed.h>
#include <string.h>


void compute_bounding_box(float predict_box[5])
{
    int batch_size = 1;
    int num_anchors = 2;
    int h = 20;
    int w = 40;

    FIX_32_4 box[4] = {1.4940052559648322, 2.3598481287086823, 4.0113013115312155, 5.760873975661669};

    FIX_32_4 conf_thresh = 0.0;
    int conf_j = 0;
    int conf_m = 0;
    int conf_n = 0;

    FIX_32_4 conf_box1 = 0.0;
    FIX_32_4 conf_box2 = 0.0;

    for(int m = 1; m <= h; m++){
        for(int n = 1 ;n <= w; n++){
            conf_box1 = (FIX_32_25)1 / ((FIX_32_25)1 + my_exp_fix(-FM_buf2[4][m][n]));
            if(conf_box1 > conf_thresh){
				conf_thresh = conf_box1;
				conf_j = 0;
				conf_m = m;
				conf_n = n;

            }
        }
    }

    for(int m = 1; m <= h; m++){
        for(int n = 1; n <= w; n++){
            conf_box2 = (FIX_32_25)1 / ((FIX_32_25)1 + my_exp_fix(-FM_buf2[9][m][n]));
            if(conf_box2 > conf_thresh){
                conf_thresh = conf_box2;
                conf_j = 1;
                conf_m = m;
                conf_n = n;
            }
        }
    }

    if( conf_j == 0 ) {
        // first bounding box
        predict_box[0] = (FIX_32_25)1 / ((FIX_32_25)1 + my_exp_fix(-FM_buf2[0][conf_m][conf_n])) + (FIX_32_25)(conf_n-1);
        predict_box[1] = (FIX_32_25)1 / ((FIX_32_25)1 + my_exp_fix(-FM_buf2[1][conf_m][conf_n])) + (FIX_32_25)(conf_m-1);
        predict_box[2] = my_exp_fix(FM_buf2[2][conf_m][conf_n]) * box[0];
        predict_box[3] = my_exp_fix(FM_buf2[3][conf_m][conf_n]) * box[1];
        predict_box[4] = conf_thresh;
    }
    else if( conf_j == 1 ) {
        // second bounding box
        predict_box[0] = (FIX_32_25)1 / ((FIX_32_25)1 + my_exp_fix(-FM_buf2[5][conf_m][conf_n])) + (FIX_32_25)(conf_n-1);
        predict_box[1] = (FIX_32_25)1 / ((FIX_32_25)1 + my_exp_fix(-FM_buf2[6][conf_m][conf_n])) + (FIX_32_25)(conf_m-1);
        predict_box[2] = my_exp_fix(FM_buf2[7][conf_m][conf_n]) * box[2];
        predict_box[3] = my_exp_fix(FM_buf2[8][conf_m][conf_n]) * box[3];
        predict_box[4] = conf_thresh;
    }


#ifdef CSIM_DEBUG
    printf("PL output:\n");
    printf("conf_m: %d, conf_n:%d\n\n", conf_m-1, conf_n-1);



	printf("%f\n", predict_box[0] / w);
	printf("%f\n", predict_box[1] / h);
	printf("%f\n", predict_box[2] / w);
	printf("%f\n", predict_box[3] / h);
	printf("%f\n", predict_box[4]);


	int x1, y1, x2, y2;
	predict_box[0] = predict_box[0] / w;
	predict_box[1] = predict_box[1] / h;
	predict_box[2] = predict_box[2] / w;
	predict_box[3] = predict_box[3] / h;

	x1 = (unsigned int)(((predict_box[0] - predict_box[2]/2.0) * 640));
	y1 = (unsigned int)(((predict_box[1] - predict_box[3]/2.0) * 360));
	x2 = (unsigned int)(((predict_box[0] + predict_box[2]/2.0) * 640));
	y2 = (unsigned int)(((predict_box[1] + predict_box[3]/2.0) * 360));

	printf("%d %d %d %d\n", x1, y1, x2, y2);
#endif


}


