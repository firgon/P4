from Model import Serializable
from datetime import date, datetime
from Model.player import Player
from Model.round import Round
from Model.match import Match


class Tournament(Serializable):
    """ Tournament record all datas about a tournament

            :param name: str
            :param place: str
            :param dates:list
            :param time_control_choice: int in tuple-keys time_control_type
                                        or str in tuple time_control_type
            :param nb_rounds: int max rounds in this tournament
            :param description free string to record any information
            :param players: a list of already signed in players
            :param rounds : list of rounds
            :param points : dict as player:points
            :param already_played : dict as player:list of players
            """

    time_control_types = ("bullet", "blitz", "coup rapide")
    # BULLET = 0
    # BLITZ = 1
    # COUPRAPIDE = 2

    """ Tuple with needed information to create a Tournament as :
    'label' displayed to help user giving informations,
    'type' of datas needed like :
    str-> I need a str
    int-> I need a int
    4 -> I need a int and 4 is default value
    list[int] -> I need a list of int
    tuple -> I need one of this options
    """
    needed_infos = ({'label': "Nom du tournoi", 'type': str},
                    {'label': "Lieu du tournoi", 'type': str},
                    {'label': "Date", 'type': list[date]},
                    {'label': "Type de contrôle du temps",
                     'type': time_control_types},
                    {'label': "Nombre de tours", 'type': 4},
                    {'label': "Description", 'type': str})

    def __init__(self,
                 name: str,
                 place: str,
                 dates: list,
                 time_control_choice,
                 nb_rounds=4,
                 description='',
                 players=None,
                 rounds=None,
                 points=None,
                 already_played=None):

        self.name = name
        self.place = place

        # if dates are str, convert them
        if isinstance(dates[0], str):
            for index, a_date in enumerate(dates):
                dates[index] = datetime.strptime(a_date, '%d/%m/%y')
        self.dates = dates

        # time control can be indicated as index in tuple or directly string
        if time_control_choice in range(len(Tournament.time_control_types)):
            self.time_control = \
                self.time_control_types[time_control_choice]
        elif time_control_choice in Tournament.time_control_types:
            self.time_control = time_control_choice
        else:
            self.time_control = Tournament.time_control_types[0]

        self.nb_rounds = nb_rounds
        self.description = description

        self.players = players
        if self.players is None:
            self.players = []

        self.rounds = rounds
        if self.rounds is None:
            self.rounds = []

        self.points = points

        if self.points is None:
            self.points = dict()
            for player in self.players:
                self.points[player] = 0

        self.already_played = already_played

        if self.already_played is None:
            self.already_played = dict()
            for player in self.players:
                self.already_played[player] = []

    def serialize(self):

        serialized_dates = []
        for day in self.dates:
            serialized_dates.append(day.strftime('%d/%m/%y'))

        serialized_players = []
        for player in self.players:
            serialized_players.append(player.id_in_db)

        serialized_rounds = []
        for a_round in self.rounds:
            serialized_rounds.append(a_round.serialize())

        serialized_points = dict()
        for player, point in self.points.items():
            serialized_points[player.id_in_db] = point

        serialized_already_played = dict()
        for player, players in self.already_played.items():
            serialized_already_played[player.id_in_db] = []
            for already_played in players:
                serialized_already_played[player.id_in_db].\
                    append(already_played)

        serialized_tournament = {'name': self.name, 'place': self.place,
                                 'dates': serialized_dates,
                                 'time_control': self.time_control,
                                 'nb_rounds': self.nb_rounds,
                                 'description': self.description,
                                 'players': serialized_players,
                                 'rounds': serialized_rounds,
                                 'points': serialized_points,
                                 'already_played': serialized_already_played}

        return serialized_tournament

    @staticmethod
    def deserialize(serialized_tournament, players_by_id: dict = None):
        name = serialized_tournament['name']
        place = serialized_tournament['place']
        dates = serialized_tournament['dates']
        time_control = serialized_tournament['time_control']
        nb_rounds = serialized_tournament['nb_rounds']
        description = serialized_tournament['description']
        players_id = serialized_tournament['players']
        players = []

        for player_id in players_id:
            players.append(players_by_id[player_id])

        serialized_rounds = serialized_tournament['rounds']

        rounds = []

        for serialized_round in serialized_rounds:
            rounds.append(Round.deserialize(serialized_round, players_by_id))

        serialized_points = serialized_tournament['points']

        points = dict()

        for player_id, point in serialized_points.items():
            player = players_by_id[int(player_id)]
            points[player] = point

        serialized_already_played = serialized_tournament['already_played']

        already_played = dict()

        for player_id, players_id in serialized_already_played.items():
            list_already_played = []
            for a_player_id in players_id:
                list_already_played.append(players_by_id[a_player_id])

            already_played[players_by_id[int(player_id)]] = list_already_played

        return Tournament(name,
                          place,
                          dates,
                          time_control,
                          nb_rounds,
                          description,
                          players,
                          rounds,
                          points)

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name + " à " + self.place \
               + " à partir du " + self.dates[0].strftime('%d/%m/%y') \
               + f"\n({len(self.players)} joueurs inscrits)\n"

    def add_player(self, player: Player):
        self.players.append(player)
        self.points[player] = 0
        self.already_played[player] = []

    def launch_new_round(self) -> Round:
        """create a new round and record results of previous round
            :return the created new round
        """

        round_id = len(self.rounds) + 1
        new_round = Round(f"Round n°{round_id}")
        self.rounds.append(new_round)

        ranked_players = self.get_players_ranked()

        possible_opponents = dict()

        for player in ranked_players:
            # all players not already played can be opponents
            possible_opponents[player] = \
                list(set(ranked_players)
                     - set(self.already_played[player]))

            # but a player can't play against himself
            possible_opponents[player].remove(player)

        return self.create_matches(new_round,
                                   ranked_players,
                                   possible_opponents)

    def create_matches(self, next_round: Round,
                       ranked_players: list,
                       possible_opponents: dict):
        """recursive method to find the best matches
        and add them to the Round given in parameters

            :param next_round Round containing all created matches
            :param ranked_players (a list of players,
                        ordered by rank in the tournament)
            :param possible_opponents a dict as
                        player: list of possible opponents

            :return next_round: the round with created matches

        """

        if len(ranked_players) < 2:
            # if ranked_players = 0 ou 1 stop searching
            return next_round

        new_match = None

        if len(ranked_players) == 2:
            # if ranked_players = 2 associate them
            new_match = Match(ranked_players[0],
                              ranked_players[1])
            next_round.add_match(new_match)
            return next_round

        # if a player as a unique possible opponent, create the match
        for player in ranked_players:
            if len(possible_opponents[player]) == 1:
                opponent = possible_opponents[player][0]
                new_match = Match(player, opponent)
                break

        if new_match is None:
            player = ranked_players[0]
            # for first round 1st player match with 1st of second half players
            # for next rounds 1st player match with 2nd player (if possible)
            if len(self.rounds) == 1:
                nb_players = len(ranked_players)
                opponent_ranking = round(nb_players / 2)
                opponent = ranked_players[opponent_ranking]
                new_match = Match(player, opponent)
            else:
                for opponent in ranked_players:
                    if opponent in possible_opponents[player]:
                        new_match = Match(player, opponent)
                        break

        if new_match is None:
            print("Cela ne devrait pas se produire!")
            return next_round
        else:
            next_round.add_match(new_match)
            # remove player in new match from all lists
            for player in new_match.get_players():
                ranked_players.remove(player)
                possible_opponents.pop(player)
                for possible in possible_opponents.values():
                    if player in possible:
                        possible.remove(player)

            return self.create_matches(next_round, ranked_players,
                                       possible_opponents)

    def get_players_ranked(self):
        """ Method to return a ordered list of players

            :return: an ordered list of players
                ranked by points in the tournament then by elo
        """

        return sorted(self.players,
                      key=lambda x: (self.points[x], x.elo),
                      reverse=True)

    def get_players_ranked_by_name(self):
        """ Method to return a ordered list of players

            :return: an ordered list of players
                ranked by Family Name
        """

        return sorted(self.players,
                      key=lambda x: (x.family_name.title()))

    def get_ranking_to_display(self, b_by_points: bool = True) -> list:
        """ Method to return dict of players in order to be displayed
        ordered by points or by name depending on b_by_points parameters

        :param b_by_points: True > players are ordered by points
                            False > players are ordered by Name

        :return: a dict with keys : N° (index), Player, ELO, Points
        """
        if b_by_points:
            ordered_players = self.get_players_ranked()
        else:
            ordered_players = self.get_players_ranked_by_name()

        ranking = []

        for index, player in enumerate(ordered_players, start=1):
            rank = dict()
            rank['N°'] = index
            rank['Joueur'] = player
            rank['ELO'] = player.elo
            rank['Points'] = self.points[player]
            ranking.append(rank)

        return ranking

    def get_all_rounds_to_display(self):
        table = []

        for index, a_round in enumerate(self.rounds, start=1):
            rank = dict()
            rank['N°'] = index
            rank['Round'] = a_round.name
            rank['Durée'] = a_round.get_duration()
            rank["Statut"] = "Terminé" if a_round.is_ended() else "En cours"
            table.append(rank)

        return table

    def get_all_matches_to_display(self):
        table = []
        matches = []

        last_index = 0
        for a_round in self.rounds:
            matches.extend(a_round.matches)
            for index, match in enumerate(a_round.matches,
                                          start=last_index + 1):
                rank = dict()
                rank['N°'] = index
                rank['Match'] = repr(match)
                rank['Round'] = a_round.name
                rank['Score'] = match.get_score()
                table.append(rank)
                last_index = index

        return table

    def set_a_score(self, match, score1, score2):
        last_round = self.get_last_round()

        round_ended = last_round.set_score(match, score1, score2)

        if round_ended:
            self.record_results()

    def record_results(self):
        """record result of last round"""
        for match in self.get_last_round().matches:
            player1, player2 = match.get_players()
            self.points[player1] += match.get_result(player1)
            self.points[player2] += match.get_result(player2)
            self.already_played[player1].append(player2)
            self.already_played[player2].append(player1)

    def get_last_round(self) -> Round:
        if self.rounds:
            return self.rounds[-1]

        return None
