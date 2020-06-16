#include <stdio.h>
#include <fstream>
#include <iostream>
//#include "loading.h"
#include "ap_fixed.h"
//#include "layers_alexnet.h"
//#include "layers_LSTM.h"
#include "LRCN.h"
#include <cstring>
#include <string>
//array for input float data

int main(){

    ap_int <512> *reorder_data = new ap_int <512>[301050+125]; //total offset 2229123
    // Read data from binary file
	char* dest  = new char[sizeof(reorder_data)];
	std::ifstream ifs;
	ifs.open("inputs_weights.bin", std::ios::binary | std::ios::in);
	ifs.read((char*) reorder_data, sizeof(ap_int<512>)*301050);
	ifs.close();

    //initialize LRCN
    printf("initialize LRCN\n");

    printf("TB pass pointer from addr. %d \n", reorder_data);
    LRCN_top(reorder_data);

    printf("\n");
    ap_int<32> num;

    int c;
    FILE* tb_file;
    tb_file=fopen("tbtestout.txt","w");

           for(int j=0;j<15;j++)
           {
               num.range(31,0)=reorder_data[301050].range(j*32+31,j*32);
               int temp=num;
               fprintf(tb_file,"%d\n",temp);
           }

        fclose(tb_file);
    
    
    return 0;
}




