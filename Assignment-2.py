''' 
-------- University of New Haven -----------
CSCI 6651 Introduction to Python Programming
Student Id: 00983752
Student Name: Ravindrababu Behara
Github Repository: https://github.com/Ravi2257/Python_CSCI-6651

 '''
# ------ Assignment-2 --------

# Here I am importing the itertools module to use permmutations function
import itertools 

# Here I am defining a function to check if the user input is alpha or not

def is_alpha_(string_input):
    return string_input.isalpha()

# Here I am using the permutations function from itertools module to get all the permutations of the input string

def string_permutations(combinations_input):

    # Here I am creating a new variable perm to store the permutations object

    perm = itertools.permutations(combinations_input)

    # Here I am converting the permutations object to a list of strings with a new list variable perm_list

    perm_list = [''.join(p) for p in perm]
    
    return perm_list

''' Here I am defining a function to check if there is any possible word in the permutations list

I defined a logic here to check if there is any possible word in the permutations list using one of
the rule in English laguage that a word contains at least one vowel in between two consonants.

So, if any word for the permuations list satisfies this rule, then we can say that there is a possible word


'''


def any_possible_word(possible_words):

    vowels = "aeiou"
    for i in range(len(possible_words) - 2):
        if (possible_words[i] not in vowels and
            possible_words[i+1] in vowels and
            possible_words[i+2] not in vowels):
            return True
    return False

# Now I am defining main function to tak the user input and call above functions. 

def main():

    # Here I am taking the user input

    user_input = input("Enter a string: ")

    # Here I am checking if the user input is alpha or not using the function defined above

    if not is_alpha_(user_input):
        print("Good Bye!")
        return

    # Here I am calling the string_permutations function to get all the permutations from the user input

    permutations_list = string_permutations(user_input)

    print("Possible Combinations are: " ", ", permutations_list)

    # Here I am creat a word list to store the possible words from the permutations list 

    words = []

    ''' Here I am creating a loop to check each permutation in the permutations list 
        If any word matches the defined rule, it will be stored in the word list
    '''

    for perm in permutations_list:

        if any_possible_word(perm):

                words.append(perm)

    ''' Here I am using a If Else condition to print word list if there are any possible words
        or else print no possible words'''
    

    if words:
        print("Possible words are: ", words)
    else:
        print("No possible words found.")


main()