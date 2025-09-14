''' 
-------- University of New Haven -----------
CSCI 6651 Introduction to Python Programming
Student Id: 00983752
Student Name: Ravindrababu Behara
Github Repository: https://github.com/Ravi2257/Python_CSCI-6651

 '''
# ------ Assignment-3 --------

# Here I am taking a dictionary to map the grades to their respective GPA values.

grade_map = {
    "A+": 5.0, "A": 4.7, "A-": 4.3,
    "B+": 4.0, "B": 3.7, "B-": 3.3,
    "C+": 3.0, "C": 2.7, "C-": 2.3,
    "D+": 2.0, "D": 1.7, "D-": 1.3,
    "F": 0.0
}

# Here I am taking two lists, one list to store the student grades and another list is to store grades 

std_grades = []

std_gpa = []

std_no = 1

# Here I am using a while loop to take the input from the user until the user enters "Q" to quit.

while True:
        
    start = input(f"Enter student {std_no} grades (F–A+) or Q to quit: ")

    if start == "Q":
        break
    
    # Here I am splitting the input string by comma

    grade = start.split(",")

    # Here I am checking if the entered grades are valid or not
    # If the grades are invalid, I am printing an error message and asking the user to enter the grades again.

    usr_inp = True

    for j in grade:
        if j not in grade_map:
            print("Invalid grade entered. Please enter grades between F and A+.")
            usr_inp = False
            break
    
    if not usr_inp:
        continue

    # Here I am appending the grades to the stdudent grades list

    std_grades.append(grade)

    # Here I am taking  for loop to calculate the GPA for each student

    total = 0

    for k in grade:
            total = total + grade_map[k]
    gpa = total / len(grade)

    # Here I am appending the GPA to the student GPA list and rounding it to 2 decimal places

    std_gpa.append(round(gpa, 2))

# Here I am printing the GPA of each student once the user enters "Q" to quit

for i in range(len(std_gpa)):
    print(f"Student #{i + 1} GPA: {std_gpa[i]}")

