

#include "max.h"
#include "iostream"
int main(){
float A[40000] ;
float ret;
ap_uint<128> HP0[2500],HP1[2500],HP2[2500],HP3[2500];
for (int i=0;i<40000;i++){
A[i] = i+0.1;
std::cout<<A[i];
}

for (int i=0;i<2500;i++){
HP1[i] = 0;
HP2[i] = 0;
HP3[i] = 0;
HP0[i] = 0;
}

for (int x=0;x<2500; x++){
for (int y=0; y<4; y++){
HP0[x] =  (HP0[x]<<y*32) + A[x*4+y];
HP1[x] =  (HP1[x]<<y*32) + A[x*4+y+10000];
HP2[x] =  (HP2[x]<<y*32) + A[x*4+y+20000];
HP3[x] =  (HP3[x]<<y*32) + A[x*4+y+30000];
std::cout<<HP0[x]<<"\n";
}
}
int size ;
size = 40000;

max(HP0,HP1,HP2,HP3,&size,&ret);
std::cout<<ret;
return 0;
}