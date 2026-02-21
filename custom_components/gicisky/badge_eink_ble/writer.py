"""Badge e-ink writer module for BLE image transmission."""

from __future__ import annotations

import logging
from io import BytesIO

import numpy as np
from PIL import Image
from bleak import BleakClient
from bleak_retry_connector import establish_connection

from . import etag as _etag
from . import rle as _rle

_LOGGER = logging.getLogger(__name__)

# BLE characteristic UUIDs for badge e-ink
CHAR_WRITE = "00001525-1212-efde-1523-785feabcd123"
CHAR_NOTIFY = "00001526-1212-efde-1523-785feabcd123"


async def update_image(
    ble_device,
    image_bytes: bytes,
    width: int = 800,
    height: int = 480,
) -> bool:
    """Send image to badge e-ink device via BLE.

    Args:
        ble_device: BleakDevice to connect to
        image_bytes: PNG/JPEG image data as bytes
        width: Target image width
        height: Target image height

    Returns:
        True if successful, False otherwise
    """
    client: BleakClient | None = None
    try:
        client = await establish_connection(
            BleakClient, ble_device, ble_device.address, timeout=10.0
        )

        # Convert image to ETAG format
        image_payload = _prepare_etag_bytes_from_png(image_bytes, target_w=width, target_h=height)

        # Send via BLE
        await _ble_send(client, ble_device.address, image_payload)
        return True

    except Exception as e:
        _LOGGER.error(f"Failed to update image on {ble_device.address}: {e}")
        return False
    finally:
        if client:
            try:
                if client.is_connected:
                    await client.disconnect()
            except Exception as e:
                _LOGGER.warning(f"Failed to disconnect from {ble_device.address}: {e}")


def _prepare_etag_bytes_from_png(
    png_bytes: bytes, target_w: int = 800, target_h: int = 480
) -> bytes:
    """Convert PNG/JPEG image bytes to device ETAG payload.

    Args:
        png_bytes: Image data as bytes
        target_w: Target width for resizing
        target_h: Target height for resizing

    Returns:
        Raw bytes ready for BLE transmission
    """
    # Open image from bytes
    im = Image.open(BytesIO(png_bytes)).convert("RGB")
    # Resize using high-quality filter
    im = im.resize((target_w, target_h), Image.LANCZOS)
    arr = np.array(im)

    # Build black plane: pixels with low luminance
    lum = 0.2126 * arr[:, :, 0] + 0.7152 * arr[:, :, 1] + 0.0722 * arr[:, :, 2]
    black_mask = (lum < 200).astype(np.uint8)

    # Build red plane: pixels where red is dominant
    red_mask = (
        (arr[:, :, 0] > arr[:, :, 1])
        & (arr[:, :, 0] > arr[:, :, 2])
        & (arr[:, :, 0] > 100)
    ).astype(np.uint8)

    # Flatten and encode using RLE
    flat_black = black_mask.reshape(-1)
    flat_red = red_mask.reshape(-1)

    black_rle = _rle.encode(flat_black)
    red_rle = _rle.encode(flat_red)

    # Build headers and concatenate
    hdr_black = _etag.build_black_plane_header(target_w, target_h, len(black_rle))
    hdr_red = _etag.build_red_plane_header(target_w, target_h, len(red_rle))

    image_data = hdr_black + bytes(black_rle) + hdr_red + bytes(red_rle)
    return image_data


async def _ble_send(client: BleakClient, address: str, image_bytes: bytes) -> None:
    """Send image bytes via BLE.

    Args:
        client: Connected BleakClient
        address: Device MAC address
        image_bytes: Image payload to send
    """
    import asyncio
    
    xor_value = _etag.compute_xor_value(address)
    header = _etag.build_header(len(image_bytes), xor_value)
    packets = _etag.split_image_in_packets(image_bytes, xor_value)

    _LOGGER.debug(f"Sending image to {address}: {len(image_bytes)} bytes, {len(packets)} packets")

    # Start notifications (some devices may not support this)
    try:
        await client.start_notify(CHAR_NOTIFY, lambda s, d: None)
    except Exception:
        _LOGGER.debug("start_notify not supported on this device")

    # Send header
    await client.write_gatt_char(CHAR_WRITE, header, response=False)
    _LOGGER.debug(f"Header sent ({len(header)} bytes)")
    
    # Wait for device to process header
    await asyncio.sleep(0.05)

    # Send all packets
    for i, pkt in enumerate(packets, start=1):
        await client.write_gatt_char(CHAR_WRITE, pkt, response=False)
        # Small delay to avoid BLE write queue overflow
        await asyncio.sleep(0.05)  # Increased from 0.02 to 0.05 seconds (50ms) for reliability
    
    _LOGGER.debug(f"All {len(packets)} packets sent successfully")
