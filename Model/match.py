from Model import Serializable
from Model.player import Player


class Match(Serializable):
    # constants to define position in list "opponent1 and opponent2
    PLAYER = 0
    SCORE = 1

    def __init__(self, player1: Player, player2: Player, score1=0, score2=0):
        self.match = ([player1, score1], [player2, score2])

    def __str__(self):
        return str(self.match[0][self.PLAYER]) \
               + " Vs " \
               + str(self.match[1][self.PLAYER])

    def set_score(self, score1: int, score2: int):
        self.match[0][Match.SCORE] = score1
        self.match[1][Match.SCORE] = score2

    def get_infos(self):
        """return a tuple with needed information to modify this Player"""
        return ({'label': "instance de classe", 'type': self},
                {'label': f"Score pour {self.match[0][Match.PLAYER]}",
                    'type': int},
                {'label': f"Score pour {self.match[1][Match.PLAYER]}",
                 'type': int})

    def get_players(self):
        return self.match[0][self.PLAYER], self.match[1][self.PLAYER]

    def get_result(self, player):
        if player in self.match[0]:
            return self.calculate_result()
        elif player in self.match[1]:
            return 1 - self.calculate_result()
        else:
            print("Ce joueur ne participe pas à ce match !")

    def get_players(self):
        return [self.match[0][Match.PLAYER], self.match[1][Match.PLAYER]]

    def calculate_result(self):
        """return 1 if player1 wins, 0 if player2 wins, 0.5 if tied"""
        if self.match[0][Match.SCORE] > self.match[1][Match.SCORE]:
            return 1
        elif self.match[0][Match.SCORE] < self.match[1][Match.SCORE]:
            return 0
        else:
            return 0.5

    def serialize(self):
        player1 = self.match[0][Match.PLAYER]
        player2 = self.match[1][Match.PLAYER]
        return {
            "player1": player1.id_in_db,
            "player2": player2.id_in_db,
            "score1": self.match[0][Match.SCORE],
            "score2": self.match[1][Match.SCORE]
        }

    @staticmethod
    def deserialize(serialized_instance, player_list):
        player1_id = serialized_instance['player1']
        player2_id = serialized_instance['player2']

        player1 = None
        player2 = None

        for player in player_list:
            if player.id_in_db == player1_id:
                player1 = player
            elif player.id_in_db == player2_id:
                player2 = player

        score1 = serialized_instance["score1"]
        score2 = serialized_instance["score2"]

        return Match(player1, player2, score1, score2)
