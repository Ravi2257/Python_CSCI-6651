''' 
-------- University of New Haven -----------
CSCI 6651 Introduction to Python Programming
Student Id: 00983752
Student Name: Ravindrababu Behara
Github Repository: https://github.com/Ravi2257/Python_CSCI-6651

 '''
# ------ Assignment-5 --------

# This is the given cipher text to decrypt

ciph_text = "L#dp#kdylqj#d#juhdw#wlph#lq#FVFL/9984$##Surihvvru#Dqwrqhwwl#lv#d#Frrs#Ndw$"

# Here I am creating frequency analysis dictionary to count occurrences of each character

freq = {}

# Here I using a for loop to iterate through each character in the cipher text

for char in ciph_text:
    if char != " ":  # To ignore blank spaces
        if char in freq:    # If character already in dictionary, increment it's count
            freq[char] = freq[char] + 1
        else:
            freq[char] = 1

# Here I am converting frequency dictionary to list of tuples for better readability

freq_list = []
for letter in freq:
# Appending tuples of (character, count) to the list
    freq_list.append((letter, freq[letter]))

print("Frequency Analysis (character, count):")
print(freq_list)
print("-" * 50)

# Here I am defining a function to decrypt the cipher text using Caesar Cipher decryption method
def caesar_decrypt(text, shift):
    result = ""

# Lists of uppercase and lowercase letters
    uppercase = ['A','B','C','D','E','F','G','H','I','J','K','L','M',
                 'N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    lowercase = ['a','b','c','d','e','f','g','h','i','j','k','l','m',
                 'n','o','p','q','r','s','t','u','v','w','x','y','z']

    for char in text:
        # Checks if a char is  uppercase
        if char in uppercase:
            # Find the position of the alphabet
            pos = 0
            while pos < 26:
                if uppercase[pos] == char:
                    break
                pos = pos + 1

            # Perform the shift
            new_pos = (pos - shift) % 26
            result = result + uppercase[new_pos]

        # Check if a char is lowercase
        elif char in lowercase:
            pos = 0
            while pos < 26:
                if lowercase[pos] == char:
                    break
                pos = pos + 1

            new_pos = (pos - shift) % 26
            result = result + lowercase[new_pos]

        else:
            # Non-alphabetic characters are added unchanged
            result = result + char

    return result

# Now I am trying all possible shifts from 0 to 25
print("All Caesar Cipher shifts:")
for shift in range(26):
    print("Shift", shift, ":", caesar_decrypt(ciph_text, shift))
