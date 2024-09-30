import json

#Zone ID dictionary
with open("Safetybot\zone_id.json", "r") as file:
    zone_id = json.load(file)

#Check lowest credit in zone_id
def target_zone():

    lowest_zone = min(zone_id, key=lambda x: zone_id[x]['credits'])
    lowest_credits = zone_id[lowest_zone]['credits']

    print(f"The zone with the lowest credits is {lowest_zone} with {lowest_credits} credits.")

    #credit increase
    zone_count = len(zone_id)
    credit_increase = zone_count*zone_id[lowest_zone]['risk_factor']
    
    zone_id[lowest_zone]['credits'] += credit_increase
    #print(f"Updated {lowest_zone} credits: {zone_id[lowest_zone]['credits']}")

    #credit decrease
    for zone in zone_id:
        zone_id[zone]['credits'] -= 1 #decrease all zones with 1 credit
        print(f"Updated {zone} credits: {zone_id[zone]['credits']}")

for i in range(15):
    print(f"\nIteration {i + 1}:")
    target_zone()