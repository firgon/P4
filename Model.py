class Player:

    MALE = 0
    FEMALE = 1
    DK = 2

    def __init__(self,
                 family_name: str,
                 first_name: str,
                 birth_date: str,
                 sex: int,
                 elo: int):
        self.family_name = family_name
        self.first_name = first_name
        self.birth_date = birth_date
        self.sex = sex
        self.elo = elo


class Tournament:
    tuple_time_control_type = ("bullet", "blitz", "coup rapide")
    BULLET = 0
    BLITZ = 1
    COUPRAPIDE = 2

    def __init__(self,
                 name: str,
                 place: str,
                 date: list,
                 time_control_choice: int,
                 nb_turn=4,
                 description=''):
        """ Constructeur de Tournament

        :type name: str
        :type place: str
        :type date:list
        :type time_control_choice: int
        :type place: str
        """

        self.name = name
        self.place = place
        self.date = date

        # if time control choice is not a known choice, default is BULLET
        if (time_control_choice >= 0) & \
                (time_control_choice < len(self.tuple_time_control_type)):
            self.time_control = \
                self.tuple_time_control_type[time_control_choice]
        else:
            self.time_control = self.BULLET

        self.nb_turn = nb_turn

        self.turns = []
        self.players = []
        self.description = description

    def add_player(self, player: Player):
        self.players.append(player)

    def launch_new_turn(self):
        if len(self.turns) == self.nb_turn:
            print("Le tournoi est terminé")
            return

        pass


class Score:

    def __init__(self, score=0):
        self._score = score

    def set_score(self, score):
        self._score = score

    def get_score(self):
        return self._score


class Match:

    # constants to define position in tuple "opponent1 and opponent2
    PLAYER = 0
    SCORE = 1

    def __init__(self, player1: Player, player2: Player):
        self.opponent1 = (player1, Score())
        self.opponent2 = (player2, Score())

    def set_score(self, player: Player, score: int):
        if player in self.opponent1:
            self.opponent1[Match.SCORE].set_score(score)
        elif player in self.opponent2:
            self.opponent2[Match.SCORE].set_score(score)
        else:
            print("Ce joueur ne participe pas à ce match !")

    def get_players(self):
        return self.opponent1[self.PLAYER], self.opponent2[self.PLAYER]

    def get_result(self, player):
        if player in self.opponent1:
            return self.calculate_result()
        elif player in self.opponent2:
            return 1-self.calculate_result()
        else:
            print("Ce joueur ne participe pas à ce match !")

    def calculate_result(self):
        """return 1 if player1 wins, 0 if player2 wins, 0.5 if tied"""
        if self.opponent1[Match.SCORE].getScore() > self.opponent2[Match.SCORE].getScore():
            return 1
        elif self.opponent1[Match.SCORE].getScore() < self.opponent2[Match.SCORE].getScore():
            return 0
        else:
            return 0.5


class Round:

    def __init__(self, name: str):
        self.name = name
        self.matches = []

    def add_match(self, player1: Player, player2: Player):
        match = Match(player1, player2)
        self.matches.append(match)
