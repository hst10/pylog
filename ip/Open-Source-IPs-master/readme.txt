Copyright (c) <2019>
<University of Illinois at Urbana-Champaign>
All rights reserved.

Developed by:  
<ES CAD Group>
<University of Illinois at Urbana-Champaign>
<http://dchen.ece.illinois.edu/>


This IP Package includes an open-source IP repository specifically designed for machine learning applications. 

The IPs include:

Standard convolution IPs
Depth-wise separable convolution IPs
Pooling IPs
Bounding box regression IP
Long-term Recurrent Convolutional Network IP

Each IP is provided with: introduction, interface description, inputs and outputs description, parameter configuration, and resource and performance. The IPs are developed in C/C++. The source code is synthesizable through Xilinx Vivado High Level Synthesis (Vivado HLS), and Register Transfer Level (RTL) code can be generated conveniently using Vivado HLS.

This project is sponsored by Semiconductor Research Corporation (SRC) through a collaborative research project between University of Illinois at Urbana-Champaign and Cornell University. The IPs developed by Cornell university can be found in the following GitHub:

https://github.com/cornell-zhang/rosetta

When referencing this particular IP Package in a publication, please use the following citation:

[1] Xinheng Liu, Cong Hao, and Deming Chen, "HLS based Open-Source IPs for Deep Neural Network Acceleration," University of Illinois at Urbana-Champaign, Feb. 2019: https://github.com/DNN-Accelerators/Open-Source-IPs

Specifically, the LRCN IP was created through the following work: 

[2] X. Zhang, X. Liu, A. Ramachandran, C. Zhuge, S. Tang, P. Ouyang, Z. Cheng, K. Rupnow and D. Chen, “High-Performance Video Content Recognition with Long-term Recurrent Convolutional Network for FPGA”, Proceedings of International Conference on Field-Programmable Logic and Applications, September 2017.

The Standard convolution, Depth-wise separable convolution, Pooling, and Bounding box regression IPs were created through the following work:

[3] C. Hao, X. Zhang, Y. Li, S. Huang, J. Xiong, K. Rupnow, W.M. Hwu, and D. Chen, “FPGA/DNN Co-Design: An Efficient Design Methodology for IoT Intelligence on the Edge”, Proceedings of IEEE/ACM Design Automation Conference, June 2019.