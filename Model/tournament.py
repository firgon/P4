from Model import Serializable
from datetime import date, datetime
from Model.player import Player
from Model.round import Round


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

        serialized_tournament = {'name': self.name, 'place': self.place,
                                 'dates': serialized_dates,
                                 'time_control': self.time_control,
                                 'nb_rounds': self.nb_rounds,
                                 'description': self.description,
                                 'players': serialized_players,
                                 'rounds': serialized_rounds}

        return serialized_tournament

    @staticmethod
    def deserialize(serialized_tournament, players_list=None):
        name = serialized_tournament['name']
        place = serialized_tournament['place']
        dates = serialized_tournament['dates']
        time_control = serialized_tournament['time_control']
        nb_rounds = serialized_tournament['nb_rounds']
        description = serialized_tournament['description']
        players_id = serialized_tournament['players']
        players = []

        for player_id in players_id:
            for player in players_list:
                if player.id_in_db == player_id:
                    players.append(player)

        serialized_rounds = serialized_tournament['rounds']

        rounds = []

        for serialized_round in serialized_rounds:
            rounds.append(Round.deserialize(serialized_round, players_list))

        return Tournament(name,
                          place,
                          dates,
                          time_control,
                          nb_rounds,
                          description,
                          players,
                          rounds)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name + " à " + self.place \
               + " à partir du " + self.dates[0].strftime('%d/%m/%y') \
               + f"\n({len(self.players)} joueurs inscrits)\n"

    def add_player(self, player: Player):
        self.players.append(player)
        self.points[player] = 0
        self.already_played[player] = []

    def launch_new_round(self):
        nb_rounds = len(self.rounds)
        if nb_rounds == self.nb_rounds:
            # Tournament is over
            return None
        else:
            round_id = nb_rounds + 1
            new_round = Round(f"Round n°{round_id}")
            self.rounds.append(new_round)
            return new_round

    def get_players_ranked(self):
        """ Method to return a ordered list of players

            :return: an ordered list of players
                ranked by points in the tournament then by elo
        """

        return sorted(self.players,
                      key=lambda x: (self.points[x], x.elo),
                      reverse=True)

    def get_ranking_to_display(self):
        """ Method to return dict of players in order to be displayed

        :return: a dict with keys : N° (index), Player, ELO, Points
        """
        ordered_players = self.get_players_ranked()

        ranking = []

        for index, player in enumerate(ordered_players, start=1):
            rank = dict()
            rank['N°'] = index
            rank['Joueur'] = player
            rank['ELO'] = player.elo
            rank['Points'] = self.points[player]
            ranking.append(rank)

        return ranking

    def get_last_round(self):
        if self.rounds:
            return self.rounds[-1]
        else:
            return None
