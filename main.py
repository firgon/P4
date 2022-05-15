import Model

# premier_joueur = Model.Player("Albisser", "Emmanuel", "02/04/1980", Model.Player.MALE, 1500)

class PersonException(Exception):
    pass


class InvalidDOBPersonException(PersonException):
    pass


try:
    raise InvalidDOBPersonException("Invalid Date of Birth")
except PersonException:
    print("PersonException caught")
except InvalidDOBPersonException("Invalid Date of Birth"):
    print("InvalidDOBPersonException caught")
except Exception:
    print("Exception caught.")
