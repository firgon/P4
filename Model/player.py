from datetime import date, datetime
from Model import Serializable


class Player(Serializable):
    """Chess player

        ::param family_name: str
        ::param first_name: str
        ::param birth_date: str or date
        ::param sex: int in enumerate TUPLE_SEX (as a int index of tuple_sex)
        ::param elo: int
    """
    TUPLE_SEX = ("Homme", "Femme", "Non-renseigné")
    MALE = 0
    FEMALE = 1
    DK = 2

    """ Tuple with needed information to create a Player as :
        'label' displayed to help user giving informations,
        'type' of datas needed like :
        str-> I need a str
        int-> I need a int
        4 -> I need a int and 4 is default value
        list[int] -> I need a list of int
        tuple -> I need one of this options
        """
    needed_infos = ({'label': "Nom de famille", 'type': str},
                    {'label': "Prénom", 'type': str},
                    {'label': "Date de naissance", 'type': date},
                    {'label': "Sexe", 'type': TUPLE_SEX},
                    {'label': "Niveau", 'type': int})

    def __init__(self,
                 family_name: str,
                 first_name: str,
                 birth_date,
                 sex: int,
                 elo: int):
        self.family_name = family_name
        self.first_name = first_name
        if isinstance(birth_date, str):
            birth_date = datetime.strptime(birth_date, '%d/%m/%y')
        self.birth_date = birth_date

        # check if sex is valid value
        if isinstance(sex, int) and sex in range(len(Player.TUPLE_SEX)):
            self.sex = sex
        else:
            self.sex = Player.DK

        self.elo = elo

    def serialize(self):
        return {
            'family_name': self.family_name,
            'first_name': self.first_name,
            'birthdate': self.birth_date.strftime('%d/%m/%y'),
            'sex': self.sex,
            'elo': self.elo
        }

    @staticmethod
    def deserialize(serialized_player, player_list=None):
        player = Player(*serialized_player.values())
        player.id_in_db = serialized_player.doc_id
        return player

    def get_sex(self) -> str:
        """return string corresponding to int sex attribute"""
        return Player.TUPLE_SEX[self.sex]

    def get_infos(self):
        """return a tuple with needed information to modify this Player"""
        return ({'label': "instance de classe", 'type': self},
                {'label': "Nom de famille", 'type': self.family_name},
                {'label': "Prénom", 'type': self.first_name},
                {'label': "Sexe", 'type': Player.TUPLE_SEX},
                {'label': "Niveau", 'type': self.elo})

    def __str__(self):
        return f"{self.first_name} {self.family_name.upper()} ({self.elo})"

    def __repr__(self):
        return f"{self.first_name} {self.family_name.upper()}"

    def __hash__(self):
        return hash((self.first_name, self.family_name))

    def __eq__(self, other):
        if not isinstance(other, Player):
            return False

        return (self.first_name, self.family_name) == \
               (other.first_name, other.family_name)
