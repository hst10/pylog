/*
numpy.convolve(a, v, mode='full')
Reverse the order of elements in an array along the given axis.
The shape of the array is preserved, but the elements are reordered.

Parameters
    a : Input array. First one-dimensional input array.
    v : Second one-dimensional input array.
    mode : {‘full’, ‘valid’, ‘same’}, optional
    ‘full’: By default, mode is ‘full’. This returns the convolution at each point of overlap,
        with an output shape of (N+M-1,). At the end-points of the convolution, the signals do not
        overlap completely, and boundary effects may be seen.
    ‘same’: Mode ‘same’ returns output of length max(M, N). Boundary effects are still visible.
    ‘valid’: Mode ‘valid’ returns output of length max(M, N) - min(M, N) + 1. The convolution product is only
        given for points where the signals overlap completely. Values outside the signal boundary have no effect.
Returns
    outarray_like: A view of m with the entries of axis reversed. 
                Since a view is returned, this operation is done in constant time.
*/

#include "convolve_1d.h"

void convolve_1d(DTYPE A[SIZE_A] , DTYPE B[SIZE_B], DTYPE C[SIZE_C])
{
#pragma HLS ARRAY_PARTITION variable=A complete
#pragma HLS ARRAY_PARTITION variable=B complete
#pragma HLS ARRAY_PARTITION variable=C complete


    for (int i=0; i<SIZE_C; i++){
        #pragma HLS unroll
        C[i] = 0; 
    }

    for (int m=0; m<VAR1 ; m++){
        for (int n=0; n<VAR2 ; n++){
        #pragma HLS pipeline
            for ( int i=0; i< SIZE_C ; i=i+VAR1){
                for (int k=0; k< SIZE_B; k=k+VAR2 ){
                    if ( (i-k>=0)&&(i-k<SIZE_A-1)&&(i+m<SIZE_C)&&(k+n<SIZE_B) ){
                        C[i+m] += A[k+n]*B[i+m-k-n];         
                    }
                }
            }
        } 
    }
}








template <int p>
{{dtype}} mult_{{batch}}(     
            {% for i in range(batch-1) %}{{dtype}} a{{i}}, {{dtype}} b{{i}},
            {% endfor %}{{dtype}} a{{batch-1}}, {{dtype}} b{{batch-1}} )
{
 //#pragma HLS inline off
    {{dtype}} {% for i in range(batch-1) %}mul{{i}},{% endfor %}mul{{batch-1}};
    {% for i in range(1,log2_batch+1) %}{{dtype}} {% for j in range(((batch//(2**i)))-1)%}add{{i}}{{j}},{% endfor %}add{{i}}{{ (batch//(2**i))-1}}; 
    {% endfor %}
    {% for i in range(batch) %}mul{{i}} = a{{i}} * b{{i}};
    {% endfor %}
    {% for i in range(batch//2)%}add1{{i}} = mul{{i*2}} + mul{{i*2+1}};
    {% endfor %}    
    {% for i in range(2,log2_batch+1) %}{% for j in range(((batch//(2**i))))%}add{{i}}{{j}} = add{{i-1}}{{j*2}} + add{{i-1}}{{j*2+1}};
    {% endfor %} 
    {% endfor %}return add{{log2_batch}}0;
}



void conv_compute_buffer( 
            {{dtype}}* input,  // input_w = w_w; input_h = w_w + elem_parallel-1
            {{dtype}}* weight,
            {{dtype}} output[{{elem_parallel}}],
            int w_len
){
    #pragma HLS array_partition variable=weight complete 
    #pragma HLS array_partition variable=output complete  // cyclic factor={{batch+elem_parallel}}
   	#pragma HLS array_partition variable=input complete

    {{dtype}} ret[{{elem_parallel}}];
    #pragma HLS array_partition variable=ret complete

    {% for p in range(elem_parallel) %}ret[{{p}}]=0;
    {% endfor %}

    for (int i=0; i< w_len; i=i+{{batch}}){
    #pragma HLS pipeline   
        {% for p in range(elem_parallel) %}
        ret[{{p}}] += mult_{{batch}}<{{p}}>(
                {% for b in range(batch-1) %}input[{{p}}+i+{{b}}],weight[i+{{b}}],
                {% endfor %}input[{{p}}+i+{{batch-1}}],weight[i+{{batch-1}}]);
        {% endfor %}
    }

    {% for p in range(elem_parallel) %}output[{{p}}]= ret[{{p}}] ;
    {% endfor %}
}




void write_output_buff({{dtype}}* output_buff, int index_i, bool skip,
            {{axi_ddr_port_type}}* output_ddr_port,  {{axi_ddr_port_type}}* output_bram_port, bool is_ddr){
    if(skip) return;

    {% for p in range(elem_parallel) %}
    {{axi_ddr_port_type}} temp{{p}} = 0;
    temp{{p}}.range(31,0) = output_buff[{{p}}];
    {% endfor %}

    if (is_ddr){
        {% for p in range(elem_parallel) %}
        output_ddr_port[index_i+{{p}}] = temp{{p}};
        {% endfor %}
    }else{
        {% for p in range(elem_parallel) %}
        output_bram_port[index_i+{{p}}] = temp{{p}};
        {% endfor %}
    }
}




void load_input_buff({{dtype}}* input_buff, int index_i, bool skip,
            {{axi_ddr_port_type}}* input_ddr_port,  {{axi_ddr_port_type}}* input_bram_port, bool is_ddr, int w_len){
    if(skip) return;

    for(int i=0; i< w_len + {{elem_parallel-1}}; i++ ){
        {{axi_ddr_port_type}} temp;
        if(is_ddr){
            temp = input_ddr_port[i+index_i];
        }else{
            temp = input_bram_port[i+index_i];
        }   
        input_buff[i] = temp.range(31,0);
    }
}






void conv1d( 
        {{axi_ddr_port_type}}* input_ddr_port,
        {{axi_ddr_port_type}}* weight_ddr_port,
        {{axi_ddr_port_type}}* output_ddr_port,
        
        {{axi_bram_port_type}}* input_bram_port,
        {{axi_bram_port_type}}* weight_bram_port,
        {{axi_bram_port_type}}* output_bram_port, 
        
        int input_len_in, 
        int w_len_in,
        
        bool is_ddr_in)
{
    #pragma HLS interface m_axi port=input_ddr_port depth={{max_ddr_port_depth}} offset=slave bundle=HP1
    #pragma HLS interface m_axi port=weight_ddr_port depth={{max_ddr_port_depth}} offset=slave bundle=HP2
    #pragma HLS interface m_axi port=output_ddr_port depth={{max_ddr_port_depth}} offset=slave bundle=HP3
    
    #pragma HLS interface m_axi port=input_bram_port depth={{max_bram_port_depth}} offset=slave bundle=HP1
    #pragma HLS interface m_axi port=weight_bram_port depth={{max_bram_port_depth}} offset=slave bundle=HP2
    #pragma HLS interface m_axi port=output_bram_port depth={{max_bram_port_depth}} offset=slave bundle=HP3
    
    #pragma HLS interface s_axilite port=input_len_in
    #pragma HLS interface s_axilite port=w_len_in

    #pragma HLS interface s_axilite port=is_ddr_in
    #pragma HLS interface s_axilite port=return   

    int input_len = input_len_in ;
    int w_len = w_len_in ; 
    bool is_ddr = is_ddr_in ;

    {{dtype}} weight_buff[{{max_weight_len_power_two}}]; 
    for (int i=0; i<w_len; i++){
    #pragma HLS pipeline
        if (is_ddr){
           weight_buff_load[i]= weight_ddr_port[i];
        }else{
           weight_buff_load[i]= weight_bram_port[i];
        }
    }

    for (int i=w_len; i<{{max_weight_len_power_two}}; i++){
        weight_buff[i]= 0;
    }

    int input_buff0[{{max_weight_len+elem_parallel}}];
    int input_buff1[{{max_weight_len+elem_parallel}}];
    int output_buff0[{{elem_parallel}}];
    int output_buff1[{{elem_parallel}}];    

    load_input_buff(input_buff0, 0, 0, input_ddr_port, input_bram_port, is_ddr, input_len);

    int i;
    bool pingpong=0;
    int i_last = 0;
    
    for (i=0; i + w_len-1 < input_len; i=i+ {{elem_parallel}}){
        bool is_first = i==0;
        bool is_last = (i+w_len+{{elem_parallel-1}})>= input_len;

        int i_next = i+ {{elem_parallel}};

        if(pingpong){
            conv_compute_buffer(input_buff1, weight_buff, output_buff1, w_len);
            load_input_buff(input_buff0, i_next, is_last, input_ddr_port, input_bram_port, is_ddr, w_len);
            write_output_buff(output_buff0, i_last, is_first, output_ddr_port, output_bram_port, is_ddr);
            pingpong = 0;
        }else{
            conv_compute_buffer(input_buff0, weight_buff, output_buff0, w_len);
            load_input_buff(input_buff1, i_next, is_last, input_ddr_port, input_bram_port, is_ddr, w_len);
            write_output_buff(output_buff1, i_last, is_first, output_ddr_port, output_bram_port, is_ddr;
            pingpong = 1;
        }
        i_last = i;
    }

    if(pingpong){
         write_output_buff(output_buff0, i_last, 0, output_ddr_port, output_bram_port, is_ddr);
    }else{
        write_output_buff(output_buff0, i_last, 0, output_ddr_port, output_bram_port, is_ddr);
    }
}



