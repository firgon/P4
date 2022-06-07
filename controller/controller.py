from views.abstractview import AbstractView
from Model.match import Match
from Model.player import Player
from Model.tournament import Tournament
from controller.serializer import Serializer
import random


class Controller:
    """This class control the application

    :param view : a view (derived from AbstractView) to interact with user

    :attributes :
        tournaments : a list of Tournaments
        players : a list of players
        active_tournament : the tournament that the user is currently modifying
        active_menu : the menu that is currently active
        serializer : a Serializer instance to handle tinyDB
    """

    GENERAL_REPORTS = ["Tous les acteurs par Nom",
                       "Tous les acteurs par Elo",
                       "Tous les tournois"]
    ACTORS_BY_NAME = 0
    ACTORS_BY_ELO = 1
    ALL_TOURNAMENTS = 2

    TOURNAMENT_REPORTS = ["Classement par Points",
                          "Classement par Nom",
                          "Liste des rounds",
                          "Liste des matchs"]
    RANKING_BY_POINTS = 0
    RANKING_BY_NAME = 1
    ALL_ROUNDS = 2
    ALL_MATCHES = 3

    def __init__(self, view: AbstractView):
        self.view = view
        self.tournaments = []
        self.all_players = []
        self.active_tournament = None
        self.active_menu = None
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

        # load datas from tinyDB
        self.load()
        self.create_menu()

    def save(self):
        """ Save all players and tournaments in DB"""
        players_ids = self.serializer.save_players(self.all_players)
        tournaments_ids = self.serializer.save_tournaments(self.tournaments)

        self.view.log(f"******** {len(players_ids)} "
                      f"joueurs sauvegardés *******")
        self.view.log(f"******** {len(tournaments_ids)} "
                      f"tournois sauvegardés *******")

    def exit(self):
        """This method allows to go to one level up in the menu"""
        if self.active_menu is not None:
            self.active_menu = None
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

    def quit(self):
        """ Quit the Tournament Manager Project"""
        self.view.log('Manager de tournoi vous souhaite une bonne journée !!')
        exit()

    def ask_for_tournament_datas(self):
        """Method to ask view to display a form with tournament needed infos,
        collected datas will be send to create_tournament method"""
        self.view.display_form(Tournament.needed_infos, self.create_tournament)

    def ask_for_player_datas(self, player: Player = None):
        """Method to ask view to display a form with player needed infos,
        to modify or create a player"""
        if player is None:
            self.view.display_form(Player.needed_infos, self.create_player)
        else:
            self.view.display_form(player.get_infos(), self.modify_player)

    def ask_for_match_result(self, match: Match):
        """Method to ask view to display a form with match needed infos,
                to modify or create a player"""
        self.view.display_form(match.get_infos(),
                               self.modify_match)

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
                   "Lister les matchs du round en cours",
                   "Lancer un nouveau round",
                   "Saisir un résultat",
                   "*** résultats automatiques ***",
                   "Afficher des rapports"]
        functions_list = [self.ask_for_player_datas,
                          self.ask_for_player_choose,
                          self.list_match,
                          self.launch_new_round,
                          self.add_result,
                          self.automatic_result,
                          self.choose_tournament_report]

        self.view.display_menu("Tournoi " + str(self.active_tournament),
                               choices,
                               functions_list)

    def add_result(self):
        self.active_menu = self.add_result
        active_round = self.active_tournament.get_last_round()
        if active_round.is_ended():
            self.view.log("Ce round est terminé, "
                          "vous ne pouvez plus le modifier.")
        else:
            self.view.display_item_choice("Quel résultat voulez-vous saisir ?",
                                          active_round.matches,
                                          self.ask_for_match_result)
        self.create_menu()

    def modify_match(self, datas: list):
        """Modify a match with datas received in parameters
        :param datas : a list as [0]-> match instance
                                 [1]-> score1
                                 [2]-> score2
        """
        match = datas[0]
        score1 = datas[1]
        score2 = datas[2]
        self.active_tournament.set_a_score(match, score1, score2)

    def automatic_result(self):
        """For test purpose, that function gives random scores
        for each currently running match in the active tournament"""
        active_round = self.active_tournament.get_last_round()
        for match in active_round.matches:
            if not match.is_ended:
                self.active_tournament.set_a_score(match,
                                                   random.randint(0, 4),
                                                   random.randint(0, 4))

        self.create_menu()

    def list_match(self):
        """Display the list of matches of the last round
        of the active tournament
        """
        last_round = self.active_tournament.get_last_round()
        if last_round is not None:
            self.view.log(last_round)
        else:
            self.view.log("Le tournoi n'a pas encore commencé. "
                          "Aucun match n'a été lancé.")

        self.create_menu()

    def launch_new_round(self):
        """Check if a new round can be launched and launch it if possible"""
        # check if there is no not-ended round
        active_round = self.active_tournament.get_last_round()
        if active_round is not None and not active_round.is_ended():
            self.view.log("Vous ne pouvez pas lancer de nouveau Round, "
                          "tous les matchs ne sont pas terminés.")

        elif len(self.active_tournament.rounds) == \
                self.active_tournament.nb_rounds:
            self.view.log("Vous ne pouvez pas lancer de nouveau Round, "
                          "ce tournoi est terminé.")

        else:
            new_round = self.active_tournament.launch_new_round()
            self.view.log(new_round)

        return self.create_menu()

    def ask_for_player_choose(self):
        """display a list of players in DB but not in active Tournament,
        to add one in the active tournament"""
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
        """Add a player to active tournament"""
        self.view.log(f"OK, j'inscris {player} "
                      f"au tournoi {self.active_tournament}")

        self.active_tournament.add_player(player)

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
        """display a list of tournament, to choose one to open"""
        self.view.display_item_choice("Quel tournoi voulez-vous ouvrir ?",
                                      self.tournaments,
                                      self.open_tournament)

    def choose_player(self, players: list = None):
        """Ask view to display a list of players (All players by default),
        to choose one to be modified"""

        if players is None:
            players = self.all_players

        self.view.display_item_choice("Quel joueur voulez-vous modifier ?",
                                      players,
                                      self.ask_for_player_datas)

    def open_tournament(self, tournament: Tournament):
        """set tournament in parameter active and update menu"""
        self.active_tournament = tournament

        self.create_menu()

    def create_menu(self):
        """display menu : Main menu, Tournament Menu or Active Menu"""
        if self.active_tournament is None and self.active_menu is None:
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
                                    self.choose_general_report])
        elif self.active_menu is None:
            self.create_tournament_menu()
        else:
            self.active_menu()

    def choose_tournament_report(self):
        """display available tournament reports"""
        self.active_menu = self.choose_tournament_report
        self.view.display_item_choice("Les rapports disponibles :",
                                      Controller.TOURNAMENT_REPORTS,
                                      self.create_tournament_report)

    def create_tournament_report(self, choice: str):
        """create a displayable TOURNAMENT report,
        depending on the choice in parameter

                :param choice : could be Controller.RANKING_BY_POINTS
                                         Controller.RANKING_BY_NAME
                                         Controller.ALL_ROUNDS or
                                         Controller.ALL_MATCHES
        """
        description = str(self.active_tournament)
        description += "\n"
        description += choice + "\n"

        if choice == \
                Controller.TOURNAMENT_REPORTS[Controller.RANKING_BY_POINTS]:
            players_dict = self.active_tournament.get_ranking_to_display()

            self.view.display_table(description, players_dict)

        elif choice == \
                Controller.TOURNAMENT_REPORTS[Controller.RANKING_BY_NAME]:
            players_dict = self.active_tournament.get_ranking_to_display(False)
            self.view.display_table(description, players_dict)

        elif choice == Controller.TOURNAMENT_REPORTS[Controller.ALL_ROUNDS]:
            rounds_dict = self.active_tournament.get_all_rounds_to_display()
            self.view.display_table(description, rounds_dict)

        elif choice == Controller.TOURNAMENT_REPORTS[Controller.ALL_MATCHES]:
            matches_dict = self.active_tournament.get_all_matches_to_display()
            self.view.display_table(description, matches_dict)

        self.choose_tournament_report()

    def choose_general_report(self):
        """display available general reports"""
        self.active_menu = self.choose_general_report
        self.view.display_item_choice("Les rapports disponibles :",
                                      Controller.GENERAL_REPORTS,
                                      self.create_general_report)

    def create_general_report(self, choice: str):
        """create a displayable GENERAL report,
        depending on the choice in parameter

        :param choice : could be Controller.ACTORS_BY_ELO
                                 Controller.ACTORS_BY_NAME or
                                 Controller.ALL_TOURNAMENTS
        """
        description = "Manager de Tournoi d'Échecs\n\n"
        description += choice + "\n"

        if choice == Controller.GENERAL_REPORTS[Controller.ACTORS_BY_ELO]:
            players = sorted(self.all_players,
                             key=lambda x: x.elo,
                             reverse=True)
            players_dict = self.create_player_dict_list(players)
            self.view.display_table(description, players_dict)
        elif choice == Controller.GENERAL_REPORTS[Controller.ACTORS_BY_NAME]:
            players = sorted(self.all_players,
                             key=lambda x: x.family_name.title(),
                             reverse=False)
            players_dict = self.create_player_dict_list(players)
            self.view.display_table(description, players_dict)
        elif choice == Controller.GENERAL_REPORTS[Controller.ALL_TOURNAMENTS]:
            tournaments_to_display = []

            for index, tournament in enumerate(self.tournaments):
                string_tournament = str(tournament)
                string_tournament = string_tournament.replace("\n", " ")

                tournament_to_display = {"N°": index + 1,
                                         "Tournoi": string_tournament
                                         }
                tournaments_to_display.append(tournament_to_display)

            self.view.display_table(description, tournaments_to_display)

        self.choose_general_report()

    @staticmethod
    def create_player_dict_list(players_list) -> list:
        """create a list of dict with displayable datas on all players"""
        players_to_display = []

        for index, player in enumerate(players_list):
            player_to_display = {
                "N°": index + 1,
                "Nom": repr(player),
                "Date de naissance": player.birth_date.strftime('%d/%m/%y'),
                "Sexe": player.get_sex(),
                "Elo": player.elo
            }
            players_to_display.append(player_to_display)

        return players_to_display
