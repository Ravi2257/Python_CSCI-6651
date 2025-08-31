''' 
-------- University of New Haven -----------
CSCI 6651 Introduction to Pyton Programming
Student Id: 00983752
Student Name: Ravindrababu Behara
Github Repository: https://github.com/Ravi2257/Python_CSCI-6651

 '''
# ------ Assignment-1 --------

# Here I am assigning a string value to a variable named x

x = 'Hello, World'

# Now I want to print the value of x

print(x)

# Now I want to print the variable type of x

print(type(x))

# Now I want to use concatenation to the existing variable x by adding '1' which is a string
# Now I am creating another vairable y to assign the cancatenated value

y = x + '1'

# Here the value of x variable is not changed because we haven't change the value assigned to it. 
# We just used the value of x here to create a new variable y and assigned the concatenated value to it.

print(y)

'''
The above example explains few charateristics of strings in python

1. The strings are characters which are declared in single or double quotes.
2. The operations like concatenation (+ i.e., addition) can be performed on strings.
3. The value of a string variable won't be changed even though we careated a new variable with help of it 
   unless we assign a new value to it. 
4. The type of a string variable in python is mentioned as <class 'str'>.

'''

print(id(x))
print(id(y))

'''

For the statement "does x reference the same Object before and after",
The IDs of both x and y variables are different. Because even though we took the reference of the variable 
in creating a new variable y, the original value of the variable x hasn't changed. 

'''



