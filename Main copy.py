import runpy

def display_menu():
    print("\n=== Robot Menu ===")
    print("1. Robot status")
    print("8. Exit")
    return input("Please select an option (1-8): ")

while True:
    # Display the menu and get the user's choice
    option_number = display_menu()

    if option_number == '1':
        runpy.run_path('Safetybot\Zone_id_loader.py')

    elif option_number == '8':
        print("Exiting the program...")
        break  # Exiting the loop

    else:
        print(f"The input '{option_number}' is not valid. Please choose a valid option from the menu.")
