def check_password(password):
    return (len(password) < 8 or len([letter for letter in password if letter.isupper()]) == 0 or
            len([letter for letter in password if letter.islower()]) == 0 or
            len([letter for letter in password if letter in '_@$!%*?&']) == 0)
