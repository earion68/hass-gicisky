#!/usr/bin/env python3
"""
Diagnostic script to identify BLE characteristics of badge_eink devices.

Usage:
  python3 diagnose_badge_eink.py <MAC_ADDRESS>

Example:
  python3 diagnose_badge_eink.py 44:00:00:49:61:56
"""

import asyncio
import sys
from bleak import BleakClient

async def diagnose_device(address: str):
    """Connect and log all services/characteristics for a device."""
    print(f"\n🔍 Diagnosing device: {address}\n")
    
    try:
        async with BleakClient(address, timeout=10.0) as client:
            print(f"✅ Connected to {address}\n")
            
            services = client.services
            print(f"📋 Services ({len(services)} total):\n")
            
            for service in services:
                print(f"  Service: {service.uuid}")
                print(f"  Description: {service.description}")
                
                if service.characteristics:
                    print(f"  Characteristics ({len(service.characteristics)}):")
                    for char in service.characteristics:
                        props = ", ".join(char.properties)
                        print(f"    - {char.uuid}")
                        print(f"      Properties: {props}")
                        print(f"      Description: {char.description}")
                else:
                    print(f"  No characteristics")
                print()
            
            # Try to find badge_eink characteristics
            print("🔎 Searching for badge_eink characteristics:\n")
            found_count = 0
            
            for service in services:
                for char in service.characteristics or []:
                    uuid_lower = char.uuid.lower()
                    if "1525" in uuid_lower or "1526" in uuid_lower:
                        print(f"  ✨ Found possible badge_eink char: {char.uuid}")
                        found_count += 1
            
            if found_count == 0:
                print("  ❌ No badge_eink characteristics found (1525/1526)")
                print("\n💡 This might be normal - device might not expose these chars in discovery")
                print("   The device might use different UUIDs or have proprietary discovery")
            
            await client.disconnect()
            print(f"\n✅ Diagnosis complete")
            
    except Exception as e:
        print(f"❌ Error connecting: {e}")
        print(f"\n💡 Make sure:")
        print(f"   1. Device {address} is powered on")
        print(f"   2. Device is in pairing/advertising mode")
        print(f"   3. Address format is correct (XX:XX:XX:XX:XX:XX)")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    address = sys.argv[1]
    asyncio.run(diagnose_device(address))
