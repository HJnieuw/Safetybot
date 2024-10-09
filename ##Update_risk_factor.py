import json

# Function to update risk factors based on the number of detected hazards
def update_risk_factor(data, hazards_dict):
    for zone, hazards in hazards_dict.items():
        if zone in data:
            # Updating the risk factor based on the number of detected hazards
            new_risk_factor = data[zone]["risk_factor"] - (0.1 * hazards)
            # Ensure risk factor does not exceed 0.0 (if needed)
            data[zone]["risk_factor"] = max(new_risk_factor, 0.0)
    return data

# JSON data
with open("Safetybot\zone_id.json", "r") as file:
    zone_id = json.load(file)

# Example hazards input (zone and number of detected hazards)
detected_hazards = {
    "Zone 1": 1,  
    "Zone 2": 2,  
    "Zone 3": 3,  
    "Zone 4": 4,  
    "Zone 5": 5
}

# Update risk factors based on detected hazards
updated_json = update_risk_factor(zone_id, detected_hazards)

#  Update json file
with open("Safetybot\zone_id.json", "w") as file:
    json.dump(updated_json, file, indent=4)