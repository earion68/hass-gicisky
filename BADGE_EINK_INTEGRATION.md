# Badge e-ink Integration

This document describes the integration of badge_eink (e-ink label) support into the hass-gicisky Home Assistant component.

## Overview

The hass-gicisky component has been extended to support badge_eink type e-ink displays in addition to the original Gicisky devices. This integration allows Home Assistant to send images to both types of devices using a unified interface.

## What is Badge e-ink?

Badge e-ink is a reverse-engineered library that supports another type of e-ink display panel, distinct from Gicisky devices. These are typically:
- Fixed resolution: 800×480 pixels
- Support for black and red color planes
- Communication via Bluetooth Low Energy (BLE)
- Simple protocol for image transmission

## Architecture Changes

### New badge_eink_ble Module

A new `badge_eink_ble` module has been created within the component with the following structure:

```
custom_components/gicisky/badge_eink_ble/
├── __init__.py          # Module exports
├── parser.py            # BLE device parsing
├── writer.py            # BLE image transmission
├── etag.py              # ETAG protocol implementation
├── rle.py               # RLE encoding/decoding
├── const.py             # Constants
└── py.typed             # Type hints marker
```

### Device Type Detection

The system automatically detects device type based on:

1. **BLE Characteristics**: Badge e-ink devices expose specific UUIDs:
   - `00001525-1212-efde-1523-785feabcd123` (CHAR_WRITE)
   - `00001526-1212-efde-1523-785feabcd123` (CHAR_NOTIFY)

2. **Manufacturer Data**: Gicisky devices advertise with manufacturer ID `0x5053`

### Configuration

Device type is automatically stored in the config entry data under `CONF_DEVICE_TYPE`:
- `DEVICE_TYPE_GICISKY`: "gicisky"
- `DEVICE_TYPE_BADGE_EINK`: "badge_eink"

## File Changes Summary

### Core Files Modified

1. **manifest.json**
   - Updated component name to "Gicisky & Badge e-ink"
   - Added service UUID for badge_eink device discovery
   - Version bumped to 1.6.0

2. **const.py**
   - Added device type constants
   - Added BLE characteristic UUIDs for badge_eink

3. **config_flow.py**
   - Added device type detection logic
   - Updated to support both device parsers
   - Device type stored in config entry data

4. **__init__.py**
   - Imports both gicisky and badge_eink update functions
   - Creates appropriate device data based on type
   - Routes image updates to correct device handler

5. **coordinator.py**
   - Updated type hints to support both device types

### Platform Files Modified

All platform entity files were updated to handle both device types:

- **camera.py** - Uses device type for appropriate naming
- **sensor.py** - Duration sensor uses device type
- **image.py** - Uses device type for entity names
- **text.py** - Uses device type for entity names

Binary sensors and regular sensors are not affected on badge_eink devices since they don't provide sensor data.

## Usage

### Device Discovery

Both device types are discovered automatically during Home Assistant's Bluetooth discovery:

1. Gicisky devices: Detected via manufacturer ID
2. Badge e-ink devices: Detected via service UUIDs

### Image Updates

When sending images to devices, the system automatically:

1. Detects the device type from the config entry
2. Selects the appropriate image conversion logic
3. Routes to the correct BLE transmission function

**Gicisky devices:**
- Support device-specific compression
- Color thresholding based on device characteristics
- Retry logic with configurable delays

**Badge e-ink devices:**
- Fixed 800×480 resolution
- Simple luminance-based black plane detection
- Red plane based on red channel dominance
- RLE-encoded transmission

### Entity Naming

Entities are named based on device type:

| Entity | Gicisky | Badge e-ink |
|--------|---------|-------------|
| Camera | Gicisky XXX Preview Content | Badge e-ink XXX Preview Content |
| Image | Gicisky XXX Last Updated Content | Badge e-ink XXX Last Updated Content |
| Duration | Gicisky XXX Write Duration | Badge e-ink XXX Write Duration |
| Alias | Gicisky XXX Alias | Badge e-ink XXX Alias |

## Technical Details

### Image Transmission Protocol (Badge e-ink)

1. **Image Conversion**
   - PNG/JPEG → RGB array
   - Resize to target dimensions (default: 800×480)
   - Generate black plane (luminance < 200)
   - Generate red plane (red > green AND red > blue AND red > 100)

2. **RLE Encoding**
   - Flatten pixel arrays to 1D
   - Apply RLE encoding (run-length encoding)
   - Build ETAG headers with dimensions

3. **BLE Transmission**
   - Compute XOR value from device MAC address
   - Build transaction header
   - Split into 200-byte packets
   - Write sequentially with 20ms delays

### Image Transmission Protocol (Gicisky)

Gicisky devices use a proprietary protocol with:
- Device-specific compression algorithms
- Configurable thresholds for black and red planes
- Support for various display resolutions
- Retry logic for failed transmissions

## Backward Compatibility

All changes are backward compatible:

- Existing Gicisky configurations continue to work unchanged
- New badge_eink devices are auto-detected
- Device type is optional (defaults to Gicisky)
- Platform files handle both types gracefully

## Future Enhancements

Possible improvements:
- Support for more badge_eink display resolutions
- Adaptive threshold detection for red plane
- Battery monitoring for badge_eink devices
- Bidirectional communication support

## Testing

To verify the integration:

1. **Device Discovery**
   - Add a badge_eink device to your Home Assistant instance
   - Verify it's detected and shows under Bluetooth devices

2. **Entity Creation**
   - Check that camera, image, and text entities are created
   - Verify names show "Badge e-ink" instead of "Gicisky"

3. **Image Updates**
   - Use the `gicisky.write` service to send images
   - Monitor logs for successful transmission
   - Verify image appears on the physical device

## Troubleshooting

### Device Not Discovered

- Ensure badge_eink device is powered and in pairing mode
- Check if BLE characteristic UUIDs match expected values
- Look for errors in Home Assistant logs

### Image Update Fails

- Verify device is in range and connected
- Check BLE signal strength
- Review `write_delay_ms` setting (try increasing)
- Enable debug logging for detailed error messages

### Wrong Entity Names

- Restart Home Assistant (entity type is cached)
- Check config entry for correct `device_type` value
- Manually edit config entry if needed

## References

- Badge e-ink Library: Reverse-engineered protocol implementation
- Gicisky Component: Original Home Assistant integration
- Home Assistant Bluetooth: Official documentation
