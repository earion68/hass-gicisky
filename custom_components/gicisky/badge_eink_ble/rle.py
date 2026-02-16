"""Badge e-ink RLE (Run-Length Encoding) implementation."""

import numpy as np


def decode(data):
    """Decode RLE-encoded data for badge e-ink format.
    
    Args:
        data: RLE encoded byte data
        
    Returns:
        Decoded 2D array (480x800 format expected)
    """
    in_ptr = 0
    out_ptr = 0
    out_data = np.zeros((480 * 800), dtype=np.uint8)
    
    while in_ptr < len(data):
        sb = data[in_ptr]
        if sb & 0x80 == 0x80:
            # Non-RLE data - 7 pixels directly encoded
            in_ptr = in_ptr + 1
            for i in range(0, 7):
                out_data[out_ptr + i] = (sb & (1 << (6 - i))) != 0
            out_ptr = out_ptr + 7
        else:
            # RLE encoded data
            rle_length = 0
            px_value = (sb & 0x40) != 0
            
            if sb & 0x40 == sb:
                # 3-byte RLE: length is next 2 bytes
                rle_length = data[in_ptr + 1] + (data[in_ptr + 2] << 8)
                in_ptr = in_ptr + 3
            elif sb & 0x41 == sb:
                # 2-byte RLE: length is next 1 byte
                rle_length = data[in_ptr + 1]
                in_ptr = in_ptr + 2
            else:
                # 1-byte RLE: length is in lower 5 bits
                rle_length = sb & 0x1F
                in_ptr = in_ptr + 1
            
            out_data[out_ptr : out_ptr + rle_length] = px_value
            out_ptr = out_ptr + rle_length
    
    return out_data.reshape(480, 800)


def encode(data):
    """Encode data using RLE (Run-Length Encoding) for badge e-ink format.
    
    Args:
        data: Input data to encode (1D array of pixel values)
        
    Returns:
        RLE encoded byte data
    """
    in_ptr = 0
    out_data = bytearray()
    
    while in_ptr < len(data):
        cur_value = data[in_ptr]
        cur_run = 0
        
        while True:
            read_ptr = in_ptr + cur_run
            if read_ptr >= len(data) or data[read_ptr] != cur_value or cur_run >= 0xFFFF:
                # Encode the run
                bit = 1 if cur_value != 0 else 0
                
                if cur_run >= 7:
                    if cur_run <= 31:
                        # 1-byte RLE
                        out_data += bytes([(bit << 6) + cur_run])
                    elif cur_run <= 255:
                        # 2-byte RLE
                        out_data += bytes([(bit << 6) + 1, cur_run])
                    else:
                        # 3-byte RLE
                        out_data += bytes([(bit << 6), (cur_run & 0xFF), ((cur_run >> 8) & 0xFF)])
                    in_ptr = in_ptr + cur_run - 1
                else:
                    # Non-RLE: encode 7 pixels directly
                    bits = 0
                    for i in range(0, 7):
                        if in_ptr + i < len(data):
                            bit_value = 1 if (data[in_ptr + i] != 0) else 0
                            if i == 0:
                                bits = bit_value << 6
                            else:
                                bits = bits | (bit_value << (6 - i))
                    out_data += bytes([(0x80 | bits)])
                    in_ptr = in_ptr + 6
                
                break
            cur_run = cur_run + 1
        
        in_ptr = in_ptr + 1
    
    return out_data
