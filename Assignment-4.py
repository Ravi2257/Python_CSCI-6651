''' 
-------- University of New Haven -----------
CSCI 6651 Introduction to Python Programming
Student Id: 00983752
Student Name: Ravindrababu Behara
Github Repository: https://github.com/Ravi2257/Python_CSCI-6651

 '''
# ------ Assignment-4 --------

# Here I am importing the math module to use the sqrt function to calculate the distance between two points.

import math

# Here I am creating a list to store the names and points entered by the user.

points = []

print("Enter name and points. Enter Q to quit.")

# Here I am using a while loop to take the input from the user until the user enters "Q" or "q" to quit.

while True:
    name = input("Enter Point Name > ")
    if name == 'q' or name == 'Q':
        break
    
    # Here I am taking the x, y and z coordinates of the point from the user.
    # I am also checking if the entered coordinates are valid numbers or not.

    x = input("Enter X > ")
    while not x.isnumeric():
        print("Invalid input, please enter a number for X.")
        x = input("Enter X > ")
    y = input("Enter Y > ")
    while not y.isnumeric():
        print("Invalid input, please enter a number for Y.")
        y = input("Enter Y > ")
        continue
    z = input("Enter Z > ")
    while not z.isnumeric():
        print("Invalid input, please enter a number for Z.")
        z = input("Enter Z > ")

    # Here i am converting the entered coordinates to float and appending the name and coordinates to the points list.

    x = float(x)
    y = float(y)
    z = float(z)

    points.append([name, (x, y, z)])


# Here I am creating a list to store the distances between points

result = []

# Here I am using a nested for loop to calculate the distance between each pair of points using the given distance formula.
for i in range(len(points)):
    for j in range(i + 1, len(points)):
        p1 = points[i]
        p2 = points[j]
        x1, y1, z1 = p1[1]
        x2, y2, z2 = p2[1]
        distance = math.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)
        result.append([f"Distance {p1[0]} to {p2[0]}", round(distance, 3)])

# Here I am printing the results

print("\nResults")
for r in result:
    print(f"{r[0]} is {r[1]:.3f}")
