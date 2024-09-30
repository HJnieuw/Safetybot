import Defining_target
import Hazard_dashboard
import Update_risk_factor
import Zone_id_loader
#import Hazard_recognition
#import Optimal_route


def display_menu():
    print("\n=== Robot Menu ===")
    print("1. Robot status")
    print("2. Stop robot")
    print("3. Pause robot")
    print("4. Change zone_ID")
    print("5. Show zone information")
    print("6. Import new site plan")
    print("7. Return")
    return input("Please select an option (1-7): ")

while True:
    # Run the Defining_target function in the loop (as per your logic)
    Defining_target()
    #Optimal_route()
    #Hazard_recognition()
    Update_risk_factor()
    Hazard_dashboard()
    
    # Display the menu and get the user's choice
    option_number = display_menu()

    # Process the user's input
    if option_number == '1':
        print("Robot status:")

    elif option_number == '2':
        print("Stopping robot...")
        break

    elif option_number == '3':
        print("Pausing robot...")

    elif option_number == '4':
        print("Changing zone_ID...")
        

    elif option_number == '5':
        print("Showing zone information...")
        Zone_id_loader()

    elif option_number == '6':
        print("Importing new site plan...")
        Zone_id_loader()

    elif option_number == '7':
        print("Returning to the main loop.")

    else:
        print(f"The input '{option_number}' is not a valid input. Please give a valid input from the menu.")