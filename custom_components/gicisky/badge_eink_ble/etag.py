"""Badge e-ink ETAG protocol implementation."""

import struct
import binascii

checksum_lut = [0, 32773, 32783, 10, 32795, 30, 20, 32785, 32819, 54, 60, 32825, 40, 32813, 32807, 34]

# checksum function in k3/b.java/a
def checksum(data):
    cur = 0xFFFF
    for byte in data:
        for i in range(0, 2):
            cur = checksum_lut[(cur >> 8 ^ byte) >> 4 & 0xF] ^ cur << 4
            byte = byte << 4
        cur = cur & 0xFFFF
    return cur


# header for RLE-encoded data, defined in k3/d.java
def build_black_plane_header(width, height, size):
    """Build black plane header for ETAG format."""
    return struct.pack(">BIHHI", 0xFC, 0, height - 1, width - 1, size)


def build_red_plane_header(width, height, size):
    """Build red plane header for ETAG format."""
    return struct.pack(">BIHHI", 0xFC, 0x80000000, 0x8000 | (height - 1), width - 1, size)


def compute_xor_value(address):
    """Compute XOR value from BLE MAC address."""
    address_bytes = binascii.unhexlify(address.replace(":", ""))
    xor_value = 0x31
    for i in range(0, 6):
        xor_value = xor_value ^ address_bytes[i]
    return xor_value


# Transaction header defined in k3/c.java
def build_header(size, xor_value):
    """Build transaction header for image data."""
    header = struct.pack(
        ">BB7sBIHBB", 0xFF, 0xFC, b"easyTag", 0x62, size, int(size / 200) + 1, 0x42, 0x54
    )
    header += struct.pack(">H", checksum(header))
    header = bytearray(header)
    header[9] = header[9] ^ xor_value
    header = bytes(a ^ xor_value for a in header)
    return header


def split_image_in_packets(data, xor_value):
    """Split image data into 200-byte packets with checksums and XOR encoding.

    Args:
        data: Raw image data bytes
        xor_value: XOR value derived from device MAC address

    Returns:
        List of packets ready for BLE transmission
    """
    packets = []
    n_packet = 1
    packet_size = 200

    for i in range(0, len(data), packet_size):
        packet = struct.pack(">H", n_packet) + data[i : i + packet_size]
        if len(packet) < packet_size + 2:
            # Pad with zeros if needed
            packet += b"\x00" * ((packet_size + 2) - len(packet))
        packet += struct.pack(">H", checksum(packet))
        packets.append(bytes(a ^ xor_value for a in packet))
        n_packet += 1
    return packets
