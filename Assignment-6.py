''' 
-------- University of New Haven -----------
CSCI 6651 Introduction to Python Programming
Student Id: 00983752
Student Name: Ravindrababu Behara
Github Repository: https://github.com/Ravi2257/Python_CSCI-6651

 '''
# ------ Assignment-6 --------

# Here I am creating a list to store user account information

users = []

# Here I am using a while loop to continuously prompt for user account details

while True:
    fname = input("Enter First Name: ").strip()
    while fname == "":
        print("First Name cannot be empty.")
        fname = input("Enter First Name: ").strip()
    lname = input("Enter Last Name: ").strip()
    while lname == "":
        print("Last Name cannot be empty.")
        lname = input("Enter Last Name: ").strip()
    usrname = input("Enter Username: ").strip()
    while True: 
        if usrname == "":
            print("Username cannot be empty.")
            usrname = input("Enter Username: ")
        elif usrname in [usr[0] for usr in users]: # Here I used list comprehension to check existing usernames
            print("Username already exists. Please choose another one.")
            usrname = input("Enter Username: ")
        else:
            break

    while True:
        password = input("Enter Password: ").strip()
        while password == "":
            print("Password cannot be empty.")
            password = input("Enter Password: ").strip()

        pw_check = input("Re-enter Password: ").strip()
        if pw_check != password:
            print("Passwords do not match. Please try again.")
            continue
        break
    pw = '*' * len(password)
    print("Proposed Account: Username:", usrname, "Name:", fname, lname, "Password:", pw)

    usr_resp = input("Accept? (y/n): ")

    if usr_resp.lower() == 'y':
        users.append(list([usrname, fname, lname, pw]))
    if input("Quit? (q to exit, other key to continue): ").lower() == 'q':
        print("Final users: ", users)
        exit()
    else:
        continue