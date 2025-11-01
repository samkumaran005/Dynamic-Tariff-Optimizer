# PROJECT FOLDER STRUCTURE:
# smart-energy-scheduler/
# ├── app.py
# ├── optimizer.py
# ├── data/
# │   ├── tariffs.json
# │   └── appliances.json
# ├── static/
# │   ├── css/
# │   │   └── style.css
# │   └── js/
# │       └── script.js
# └── templates/
#     ├── base.html
#     ├── index.html
#     ├── appliances.html
#     ├── scheduler.html
#     └── dashboard.html



# ================== optimizer.py ==================
import json
from datetime import datetime, timedelta
import os

class EnergyOptimizer:
    def __init__(self):
        self.data_dir = 'data'
        self.tariff_file = os.path.join(self.data_dir, 'tariffs.json')
        self.appliances_file = os.path.join(self.data_dir, 'appliances.json')
        self.ensure_data_files()
    
    def ensure_data_files(self):
        """Create data directory and initialize JSON files if they don't exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            print(f"Created directory: {self.data_dir}")
        
        # Initialize tariffs file
        if not os.path.exists(self.tariff_file) or os.path.getsize(self.tariff_file) == 0:
            default_tariffs = {
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
            with open(self.tariff_file, 'w', encoding='utf-8') as f:
                json.dump(default_tariffs, f, indent=4)
            print(f"Created file: {self.tariff_file}")
        
        # Initialize appliances file
        if not os.path.exists(self.appliances_file) or os.path.getsize(self.appliances_file) == 0:
            default_appliances = {
                "appliances": [
                    {"id": 1, "name": "Washing Machine", "power_kw": 2.0, "duration_hours": 1.5},
                    {"id": 2, "name": "Dishwasher", "power_kw": 1.8, "duration_hours": 2.0},
                    {"id": 3, "name": "EV Charger", "power_kw": 7.0, "duration_hours": 4.0}
                ]
            }
            with open(self.appliances_file, 'w', encoding='utf-8') as f:
                json.dump(default_appliances, f, indent=4)
            print(f"Created file: {self.appliances_file}")
    
    def load_tariffs(self):
        """Load tariff data from JSON file"""
        try:
            with open(self.tariff_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading tariffs: {e}")
            # Recreate the file
            self.ensure_data_files()
            with open(self.tariff_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    
    def load_appliances(self):
        """Load appliances data from JSON file"""
        try:
            with open(self.appliances_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    # File is empty, recreate it
                    self.ensure_data_files()
                    with open(self.appliances_file, 'r', encoding='utf-8') as f:
                        return json.load(f)['appliances']
                return json.loads(content)['appliances']
        except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
            print(f"Error loading appliances: {e}")
            # Recreate the file
            self.ensure_data_files()
            with open(self.appliances_file, 'r', encoding='utf-8') as f:
                return json.load(f)['appliances']
    
    def add_appliance(self, appliance_data):
        """Add a new appliance to the list"""
        try:
            data = self.load_appliances()
            new_id = max([a['id'] for a in data], default=0) + 1
            new_appliance = {
                "id": new_id,
                "name": appliance_data['name'],
                "power_kw": float(appliance_data['power_kw']),
                "duration_hours": float(appliance_data['duration_hours'])
            }
            data.append(new_appliance)
            
            with open(self.appliances_file, 'w', encoding='utf-8') as f:
                json.dump({"appliances": data}, f, indent=4)
            
            return {"success": True, "appliance": new_appliance}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_appliance(self, appliance_id):
        """Delete an appliance from the list"""
        try:
            data = self.load_appliances()
            data = [a for a in data if a['id'] != appliance_id]
            
            with open(self.appliances_file, 'w', encoding='utf-8') as f:
                json.dump({"appliances": data}, f, indent=4)
            
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_rate_for_time(self, hour, minute=0):
        """Get the electricity rate for a specific time"""
        tariffs = self.load_tariffs()
        time_str = f"{hour:02d}:{minute:02d}"
        
        for slot in tariffs['time_slots']:
            if slot['start'] <= time_str < slot['end']:
                return slot['rate'], slot['type']
        
        # Default to first slot if no match found
        return tariffs['time_slots'][0]['rate'], tariffs['time_slots'][0]['type']
    
    def calculate_cost(self, power_kw, duration_hours, start_hour):
        """Calculate the cost of running an appliance starting at a specific hour"""
        total_cost = 0
        current_hour = start_hour
        remaining_duration = duration_hours
        
        while remaining_duration > 0:
            rate, rate_type = self.get_rate_for_time(current_hour % 24)
            
            # Calculate duration in current slot (max 1 hour)
            duration_in_slot = min(remaining_duration, 1.0)
            cost = power_kw * duration_in_slot * rate
            total_cost += cost
            
            remaining_duration -= duration_in_slot
            current_hour += 1
        
        return round(total_cost, 2)
    
    def optimize_schedule(self, appliance_ids, constraints):
        """Generate optimized schedule recommendations for selected appliances"""
        appliances = self.load_appliances()
        selected_appliances = [a for a in appliances if a['id'] in appliance_ids]
        
        recommendations = []
        
        for appliance in selected_appliances:
            slots = []
            
            # Calculate cost for each hour of the day
            for hour in range(24):
                cost = self.calculate_cost(
                    appliance['power_kw'],
                    appliance['duration_hours'],
                    hour
                )
                
                rate, rate_type = self.get_rate_for_time(hour)
                
                end_hour = (hour + int(appliance['duration_hours'])) % 24
                
                slots.append({
                    "start_time": f"{hour:02d}:00",
                    "end_time": f"{end_hour:02d}:00",
                    "cost": cost,
                    "rate_type": rate_type,
                    "savings_vs_peak": 0
                })
            
            # Sort by cost (lowest first)
            slots.sort(key=lambda x: x['cost'])
            
            # Calculate savings compared to most expensive slot
            peak_cost = max([s['cost'] for s in slots])
            for slot in slots:
                slot['savings_vs_peak'] = round(peak_cost - slot['cost'], 2)
            
            recommendations.append({
                "appliance_id": appliance['id'],
                "appliance_name": appliance['name'],
                "power_kw": appliance['power_kw'],
                "duration_hours": appliance['duration_hours'],
                "best_slots": slots[:3],  # Top 3 cheapest
                "worst_slots": slots[-3:],  # Top 3 most expensive
                "all_slots": slots
            })
        
        return recommendations
    
    def calculate_savings(self, schedule_data):
        """Calculate savings between current and optimized schedules"""
        current_schedule = schedule_data.get('current', [])
        optimized_schedule = schedule_data.get('optimized', [])
        
        current_total = sum([item['cost'] for item in current_schedule])
        optimized_total = sum([item['cost'] for item in optimized_schedule])
        
        daily_savings = current_total - optimized_total
        monthly_savings = daily_savings * 30
        yearly_savings = daily_savings * 365
        
        # Approximate CO2 reduction (0.82 kg CO2 per kWh)
        co2_reduction = daily_savings * 0.82
        
        return {
            "current_cost": round(current_total, 2),
            "optimized_cost": round(optimized_total, 2),
            "daily_savings": round(daily_savings, 2),
            "monthly_savings": round(monthly_savings, 2),
            "yearly_savings": round(yearly_savings, 2),
            "co2_reduction_kg": round(co2_reduction, 2),
            "savings_percentage": round((daily_savings / current_total * 100) if current_total > 0 else 0, 1)
        }


# ================== data/tariffs.json ==================
# This file is auto-generated by optimizer.py

# ================== data/appliances.json ==================
# This file is auto-generated by optimizer.py