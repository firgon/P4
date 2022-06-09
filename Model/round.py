from Model import Serializable
from Model.match import Match
from datetime import datetime


class Round(Serializable):

    def __init__(self, name: str, matches=None, start=None, end=None):
        self.name = name
        if matches is None:
            self.matches = []
        else:
            self.matches = matches

        if start is None:
            self.start = self.get_simpler_now()
        else:
            self.start = start

        self.end = end

    def add_match(self, match: Match):
        self.matches.append(match)

    def set_score(self, match: Match, score1: int, score2: int):
        """add a new result and check if round is ended"""
        if match in self.matches:
            match.set_score(score1, score2)
            return self.check_round_end()
        else:
            raise Exception("Ce match n'appartient pas à ce round.")

    def check_round_end(self) -> bool:
        """stop round if all matches are ended
        :return True if all matches are ended, False otherwise"""
        check = True
        for match in self.matches:
            check = check and match.is_ended

        if check:
            self.end = self.get_simpler_now()

        return check

    def __str__(self):
        value = f"{self.name} : \n"
        for match in self.matches:
            value += f"{str(match)} \n"

        if self.is_ended():
            value += f"Matchs terminés en {self.get_duration()}"
        else:
            value += f"En cours depuis : {self.get_duration()}"

        return value

    def is_ended(self):
        return self.end is not None

    @staticmethod
    def get_simpler_now():
        """return now() without microsecond"""
        return datetime.now().replace(microsecond=0)

    def get_duration(self) -> str:
        """ give duration between start and end,
        or start and now if round is not ended"""
        if not self.is_ended():

            return str(self.get_simpler_now() - self.start)
        else:
            return str(self.end - self.start)

    def serialize(self):
        serialized_matches = []
        for match in self.matches:
            serialized_matches.append(match.serialize())

        return {'name': self.name,
                'matches': serialized_matches,
                'start': self.start.strftime("%Y-%m-%d %H:%M:%S"),
                'end': None if self.end is None else self.end.strftime(
                    "%Y-%m-%d %H:%M:%S")
                }

    @staticmethod
    def deserialize(serialized_instance, players_by_id: dict = None):
        name = serialized_instance['name']
        serialized_matches = serialized_instance['matches']
        start = datetime.strptime(serialized_instance['start'],
                                  "%Y-%m-%d %H:%M:%S")

        if serialized_instance['end'] is not None:
            end = datetime.strptime(serialized_instance['end'],
                                    "%Y-%m-%d %H:%M:%S")
        else:
            end = None

        matches = []
        for serialized_match in serialized_matches:
            matches.append(Match.deserialize(serialized_match, players_by_id))

        return Round(name, matches, start, end)
