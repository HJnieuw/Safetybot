import runpy

def display_menu():
    print("\n=== Robot Menu ===")
    print("1. Robot status")
    print("2. Start robot")
    print("3. Stop robot")
    print("4. Pause robot")
    print("5. Change zone_ID")
    print("6. Show zone information")
    print("7. Import new site plan")
    print("8. Exit")
    return input("Please select an option (1-8): ")

while True:
    # Display the menu and get the user's choice
    option_number = display_menu()

    # Process the user's input
    if option_number == '1':
        zone_id = 'Zone_id.json'

        # Check if the JSON file contains any zones
        if id(zone_id):
            runpy.run_path('Defining_target.py')
            # runpy.run_path(Hazard check)  # Uncomment and define if needed
            runpy.run_path('Update_risk_factor.py')
        else:
            print("No zones available. Please update the zone file.")

    elif option_number == '2':
        print("Starting robot...")
        # Add functionality to start the robot here

    elif option_number == '3':
        print("Stopping robot...")
        break  # Exiting the loop

    elif option_number == '4':
        print("Pausing robot...")
        # Add functionality to pause the robot here

    elif option_number == '6':
        print("Showing zone information...")
        runpy.run_path('Zone_id_loader.py')

    elif option_number == '7':
        print("Importing new site plan...")
        runpy.run_path('Zone_id_loader.py')

    elif option_number == '8':
        print("Exiting the program...")
        break  # Exiting the loop

    else:
        print(f"The input '{option_number}' is not valid. Please choose a valid option from the menu.")
