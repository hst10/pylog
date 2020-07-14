
union AXI_int32
{
    std::int32_t n;     // occupies 4 bytes
    std::uint16_t s[2]; // occupies 4 bytes
    std::uint8_t c;     // occupies 1 byte
}

typedef struct { unsigned short A; unsigned char B[4]; } data_t;