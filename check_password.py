from string import ascii_letters as letters
import re


def check_password(password):
    if len(password) < 8:
        return ValueError
    password_cp = [letter for letter in password if letter.isalpha()]
    if password_cp == password:
        return ValueError
    if not password_cp[0].isupper():
        return ValueError
    password_cp = [letter for letter in password_cp if letter in letters]
    if len(password_cp) != len(password):
        return ValueError
    
