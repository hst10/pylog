set_directive_interface -mode m_axi -offset slave -depth 86400 conv2d data
set_directive_interface -mode m_axi -offset slave -depth 9     conv2d w
set_directive_interface -mode m_axi -offset slave -depth 86400 conv2d c

set_directive_pipeline conv2d/hmap_i2