"""
JSON File Fixer Script
Run this to create/fix the data files before running the main app
"""

import os
import json

def create_data_files():
    # Create data directory
    if not os.path.exists('data'):
        os.makedirs('data')
        print("✓ Created 'data' directory")
    
    # Create tariffs.json
    tariffs = {
        "tariff_plan": "Standard Time of Use",
        "currency": "₹",
        "time_slots": [
            {"start": "00:00", "end": "06:00", "rate": 4.5, "type": "off-peak"},
            {"start": "06:00", "end": "09:00", "rate": 8.0, "type": "peak"},
            {"start": "09:00", "end": "17:00", "rate": 6.0, "type": "mid-peak"},
            {"start": "17:00", "end": "22:00", "rate": 9.0, "type": "peak"},
            {"start": "22:00", "end": "24:00", "rate": 5.0, "type": "off-peak"}
        ]
    }
    
    with open('data/tariffs.json', 'w', encoding='utf-8') as f:
        json.dump(tariffs, f, indent=4, ensure_ascii=False)
    print("✓ Created 'data/tariffs.json'")
    
    # Create appliances.json
    appliances = {
        "appliances": [
            {"id": 1, "name": "Washing Machine", "power_kw": 2.0, "duration_hours": 1.5},
            {"id": 2, "name": "Dishwasher", "power_kw": 1.8, "duration_hours": 2.0},
            {"id": 3, "name": "EV Charger", "power_kw": 7.0, "duration_hours": 4.0},
            {"id": 4, "name": "Water Heater", "power_kw": 3.0, "duration_hours": 1.0},
            {"id": 5, "name": "Air Conditioner", "power_kw": 1.5, "duration_hours": 8.0}
        ]
    }
    
    with open('data/appliances.json', 'w', encoding='utf-8') as f:
        json.dump(appliances, f, indent=4, ensure_ascii=False)
    print("✓ Created 'data/appliances.json'")
    
    # Verify files
    print("\n--- Verification ---")
    try:
        with open('data/tariffs.json', 'r', encoding='utf-8') as f:
            tariff_data = json.load(f)
            print(f"✓ tariffs.json is valid - {len(tariff_data['time_slots'])} time slots")
    except Exception as e:
        print(f"✗ Error reading tariffs.json: {e}")
    
    try:
        with open('data/appliances.json', 'r', encoding='utf-8') as f:
            appliance_data = json.load(f)
            print(f"✓ appliances.json is valid - {len(appliance_data['appliances'])} appliances")
    except Exception as e:
        print(f"✗ Error reading appliances.json: {e}")
    
    print("\n✅ All files created successfully!")
    print("You can now run: python app.py")

if __name__ == "__main__":
    print("=== Smart Energy Scheduler - JSON File Fixer ===\n")
    create_data_files()