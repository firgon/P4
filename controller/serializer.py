from tinydb import TinyDB
from model.player import Player
from model.tournament import Tournament


class Serializer:
    """This class will help controller to save and load objects Tournament
    and Players"""

    def __init__(self):
        self.db = TinyDB('db.json')
        self.players_table = self.db.table('Players')
        self.tournaments_table = self.db.table('Tournaments')

    def save_players(self, players: list):
        """save tournaments
                :param players list of object Player

                :return a list of ids recorded in db
        """

        serialized_players = []

        for player in players:
            serialized_players.append(player.serialize())

        self.players_table.truncate()

        ids = self.players_table.insert_multiple(serialized_players)
        for index in range(len(ids)):
            players[index].id_in_db = ids[index]

        return ids

    def save_tournaments(self, tournaments: list):
        """save tournaments
        :param tournaments list of object Tournament

        :return a list of ids recorded in db"""
        serialized_tournaments = []

        for tournament in tournaments:
            serialized_tournaments.append(tournament.serialize())

        self.tournaments_table.truncate()

        return self.tournaments_table.insert_multiple(serialized_tournaments)

    def load_players(self):
        players = []

        serialized_players = self.players_table.all()

        for serialized_player in serialized_players:
            players.append(Player.deserialize(serialized_player, None))

        return players

    def load_tournaments(self, players_list):
        tournaments = []

        players_by_id = dict()

        for player in players_list:
            players_by_id[player.id_in_db] = player

        serialized_tournaments = self.tournaments_table.all()

        for serialized_tournament in serialized_tournaments:
            tournaments.append(Tournament.deserialize(serialized_tournament,
                                                      players_by_id))

        return tournaments
