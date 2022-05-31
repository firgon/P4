from views.abstractview import AbstractView
from Model.match import Match
from Model.player import Player
from Model.tournament import Tournament
from Model.round import Round
from controller.serializer import Serializer
import types


class Controller:
    """This class control the application

    :param view : a view to interact with user

    :attributes :
        tournaments : a list of Tournaments
        players : a list of players
        active_tournament : the tournament that the user is currently modifying
        active_player : the player that the user is currently modifying
    """

    def __init__(self, view: AbstractView):
        self.view = view
        self.tournaments = []
        self.all_players = []
        self.active_tournament = None
        self.active_player = None
        self.serializer = Serializer()

        """define commands that should be always available for user
        as a dict() given to view"""
        highest_level_commands = [
            {'short': "s",
             'long': "sauvegarder",
             'label': "pour sauvegarder les données en cours d'utilisation",
             'function': self.save},
            {'short': "c",
             'long': "charger",
             'label': "pour charger les données de la base de données",
             'function': self.load},
            {'short': "exit",
             'long': "sortir",
             'label': "pour sortir du menu en cours",
             'function': self.exit},
            {'short': "q",
             'long': "quitter",
             'label': "pour sauver et quitter le manager",
             'function': self.quit}]

        view.display_highest_level_menu(highest_level_commands)

        self.load()

    def save(self):
        """ Save all players and tournaments in DB"""
        players_ids = self.serializer.save_players(self.all_players)
        tournaments_ids = self.serializer.save_tournaments(self.tournaments)

        self.view.log(f"******** {len(players_ids)} "
                      f"joueurs sauvegardés *******")
        self.view.log(f"******** {len(tournaments_ids)} "
                      f"tournois sauvegardés *******")

        self.create_menu()

    def exit(self):
        """This method allows to go to one level up in the menu
        """
        if self.active_player is not None:
            self.active_player = None
        elif self.active_tournament is not None:
            self.active_tournament = None

        self.create_menu()

    def load(self):
        """ Load all players and tournaments from DB"""
        self.all_players = self.serializer.load_players()
        self.tournaments = self.serializer.load_tournaments(self.all_players)

        self.view.log(f"J'ai chargé une liste de "
                      f"{len(self.all_players)} joueurs ")
        self.view.log(f"J'ai chargé une liste de "
                      f"{len(self.tournaments)} tournois ")

        self.create_menu()

    def quit(self):
        """ Quit the Tournament Manager Project"""
        self.view.log('Manager de tournoi vous souhaite une bonne journée !!')
        exit()

    def ask_for_tournament_datas(self):
        """Method to ask view to display a form with tournament needed infos,
        collected datas will be send to create_tournament method"""
        self.view.display_form(Tournament.needed_infos, self.create_tournament)

    def ask_for_player_datas(self):
        """Method to ask view to display a form with player needed infos,
        collected datas will be send to create_player method"""
        self.view.display_form(Player.needed_infos, self.create_player)

    def create_tournament(self, datas):
        """create a new tournament instance according to received datas
        and make this Tournament active"""
        new_tournament = Tournament(*datas)
        self.tournaments.append(new_tournament)

        self.active_tournament = new_tournament

        self.create_menu()

    def create_player(self, datas):
        """create a new Player instance according to received datas
        and add this player to tournament if a Tournament is active"""
        new_player = Player(*datas)
        self.all_players.append(new_player)

        if self.active_tournament is not None:
            self.active_tournament.add_player(new_player)

        self.create_menu()

    def create_tournament_menu(self):
        """create a menu when the user is inside a tournament
        (active_tournament is not None)
        """
        choices = ["Créer et intégrer un nouveau joueur",
                   "Intégrer un joueur déjà en base",
                   "Afficher le classement",
                   "Lister les matchs en cours",
                   "Lancer un nouveau round",
                   "Saisir un résultat",
                   "*** résultats automatiques ***"]
        functions_list = [self.ask_for_player_datas,
                          self.ask_for_player_choose,
                          self.create_ranking,
                          self.list_match,
                          self.launch_new_round,
                          self.add_result,
                          self.automatic_result]

        self.view.display_menu("Tournoi " + str(self.active_tournament),
                               choices,
                               functions_list)

    def add_result(self):
        active_round = self.active_tournament.get_last_round()
        if active_round.is_ended():
            self.view.log("Il n'y a plus aucun match en cours.")
        else:
            self.view.display_item_choice("Quel résultat voulez-vous saisir ?",
                                          active_round.matches,
                                          self.ask_for_match_result)

    def ask_for_match_result(self, match: Match):
        self.view.display_form(match.get_infos(),
                               self.modify_match)

    def modify_match(self, datas):
        match = datas[0]
        print(datas)
        match.set_score(datas[1], datas[2])

        self.add_result()

    def automatic_result(self):
        pass

    def create_ranking(self):
        ranking = self.active_tournament.get_ranking_to_display()

        self.view.display_list(ranking)

        self.create_menu()

    def list_match(self):
        last_round = self.active_tournament.get_last_round()
        if last_round is not None:
            self.view.log(last_round)
        else:
            self.view.log("Le tournoi n'a pas encore commencé. "
                          "Aucun match n'a été lancé.")

        self.create_menu()

    def launch_new_round(self):

        # check if there is no not-ended round
        active_round = self.active_tournament.get_last_round()
        if active_round is not None and not active_round.is_ended():
            self.view.log("Vous ne pouvez pas lancer de nouveau Round, "
                          "tous les matchs ne sont pas terminés.")
            return self.create_menu()

        ranked_players = self.active_tournament.get_players_ranked()
        already_played = self.active_tournament.already_played
        is_first_round = (len(self.active_tournament.rounds) == 0)

        possible_opponents = dict()

        for player in ranked_players:
            # all players can be opponents
            possible_opponents[player] = list(ranked_players)
            # but a player can't play against himself
            possible_opponents[player].remove(player)
            # but a player can't play against already played player
            for opponent in already_played[player]:
                possible_opponents[player].remove(opponent)

        next_round = self.active_tournament.launch_new_round()

        if next_round is None:
            self.view.log("Ce tournoi est terminé !")
        else:
            next_round = self.create_matches(next_round,
                                             ranked_players,
                                             possible_opponents,
                                             is_first_round)

            self.view.log(next_round)

        return self.create_menu()

    def create_matches(self, next_round: Round,
                       ranked_players: list,
                       possible_opponents: dict,
                       is_first_round: bool):
        """Method to find the best matches
        and return them in a list given in parameters

        :param next_round Round containing all created matches
        :param ranked_players (a list of players,
                    ordered by rank in the tournament)
        :param possible_opponents a dict as
                    player: list of possible opponents
        :param is_first_round indicates if this turn is the first
                    of the tournament
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
            if is_first_round:
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
        else:
            next_round.add_match(new_match)
            # remove player in new match from all lists
            for player in new_match.get_players():
                ranked_players.remove(player)
                possible_opponents.pop(player)
                for possible in possible_opponents.values():
                    possible.remove(player)

            return self.create_matches(next_round, ranked_players,
                                       possible_opponents, is_first_round)

    def ask_for_player_choose(self):
        possible_players = []

        for player in self.all_players:
            if player not in self.active_tournament.players:
                possible_players.append(player)

        self.view.display_item_choice("Quel joueur voulez-vous intégrer ?",
                                      possible_players,
                                      self.add_player)
        #     iterate
        self.ask_for_player_choose()

    def add_player(self, player: Player):
        self.view.log(f"OK, j'inscris {player} "
                      f"au tournoi {self.active_tournament}")

        self.active_tournament.add_player(player)

    def ask_for_confirm_player_datas(self, player: Player):
        """create a menu when the user is inside a player
        (active_player is not None)
        """

        self.view.display_form(player.get_infos(), self.modify_player)

    def modify_player(self, infos):
        """modify player according to received infos

        :param : infos -> as (Player, family_name, first_name, sex, elo)"""
        player = infos[0]
        player.family_name = infos[1]
        player.first_name = infos[2]
        player.sex = infos[3]
        player.elo = infos[4]

        self.choose_player()

    def choose_tournament(self):

        self.view.display_item_choice("Quel tournoi voulez-vous ouvrir ?",
                                      self.tournaments,
                                      self.open_tournament)

    def choose_player(self, players=None):

        if players is None:
            players = self.all_players

        self.view.display_item_choice("Quel joueur voulez-vous modifier ?",
                                      players,
                                      self.ask_for_confirm_player_datas)

    def open_tournament(self, tournament: Tournament):
        self.active_tournament = tournament

        self.create_menu()

    def open_player(self, index: int):
        self.active_player = self.all_players[index]

        self.create_menu()

    def create_menu(self):
        if self.active_tournament is None and self.active_player is None:
            self.view.display_menu("Menu principal",
                                   ["Créer et ouvrir un tournoi",
                                    "Ouvrir un tournoi existant",
                                    "Créer un joueur",
                                    "Modifier un joueur",
                                    "Afficher des rapports"],
                                   [self.ask_for_tournament_datas,
                                    self.choose_tournament,
                                    self.ask_for_player_datas,
                                    self.choose_player,
                                    self.choose_report])
        elif self.active_player is None:
            self.create_tournament_menu()

    def choose_report(self):
        self.view.display_item_choice("Les rapports disponibles :",
                                      ["Les acteurs par Nom",
                                       "Les acteurs par Elo",
                                       "Les tournois"],
                                      self.create_report)

    def create_report(self, choice: str):
        if choice == "Les acteurs par Elo":
            players = sorted(self.all_players,
                             key=lambda x: x.elo,
                             reverse=True)
            players_dict = self.create_player_dict_list(players)
            self.view.display_list(players_dict)
        elif choice == "Les acteurs par Nom":
            players = sorted(self.all_players,
                             key=lambda x: x.family_name.title(),
                             reverse=False)
            players_dict = self.create_player_dict_list(players)
            self.view.display_list(players_dict)
        elif choice == "Les tournois":
            tournaments_to_display = []

            for index, tournament in enumerate(self.tournaments):
                string_tournament = str(tournament)
                string_tournament = string_tournament.replace("\n", " ")

                tournament_to_display = {"N°": index + 1,
                                         "Tournoi": string_tournament
                                         }
                tournaments_to_display.append(tournament_to_display)

            self.view.display_list(tournaments_to_display)

        self.choose_report()

    def create_player_dict_list(self, players_list) -> list:
        players_to_display = []

        for index, player in enumerate(players_list):
            player_to_display = {
                "N°": index+1,
                "Nom": repr(player),
                "Date de naissance": player.birth_date.strftime('%d/%m/%y'),
                "Sexe": player.get_sex(),
                "Elo": player.elo
            }
            players_to_display.append(player_to_display)

        return players_to_display

class Action:
    """
    Class that associate a label (:str) and an action (:function)
    """

    def __init__(self, label: str, callback):
        if not isinstance(label, str):
            raise TypeError(f"{label} is not a valid string")
        if not isinstance(callback, types.FunctionType):
            raise TypeError(f"{callback} is not a function")
        self.label = label
        self.callback = callback

    def __str__(self):
        return self.label

    def act(self):
        return self.callback()


class MultiChoiceAction(Action):
    """
        Class that associate a label_list (list of string)
        and an action (:function) that will be act
    """

    def __init__(self, label: list, callback):
        super().__init__()
        if not isinstance(label, list):
            raise TypeError(f"{label} is not a list")
        if not isinstance(callback, types.FunctionType):
            raise TypeError(f"{callback} is not function")
        self.label = label
        self.callback = callback

    def __str__(self):
        return [self.label]

    def act(self, index: int):
        return self.callback(self.label[index])
