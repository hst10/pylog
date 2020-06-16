int conv2d(float data[360][240], float w[3][3], float c[360][240])
{

  hmap_i1: for (int i1 = 1; i1 < 360; i1 += 1) {
    hmap_i2: for (int i2 = 1; i2 < 240; i2 += 1) {
      float tmp3 = 0;
      dot_i4: for (int i4 = 0; i4 < 3; i4 += 1) {
        dot_i5: for (int i5 = 0; i5 < 3; i5 += 1) {
          tmp3 += data[i4+i1+(-1)][i5+i2+(-1)] * w[i4][i5]; 
        }
      }
      c[i1][i2] = tmp3; 
    }
  }
  return 0;
}
