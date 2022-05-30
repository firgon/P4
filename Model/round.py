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

    def __str__(self):
        value = f"{self.name} : \n"
        for match in self.matches:
            value += f"{str(match)} \n"

        if self.is_ended():
            value += f"*** Matchs terminés en {self.get_duration()} ***"
        else:
            value += f"   En cours depuis : {self.get_duration():7}"

        return value

    def is_ended(self):
        return self.end is not None

    @staticmethod
    def get_simpler_now():
        """little trick to remove milliseconds in datetime"""
        string_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return datetime.strptime(string_now, "%Y-%m-%d %H:%M:%S")

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

        if self.end is None:
            return {'name': self.name,
                    'matches': serialized_matches,
                    'start': self.start.strftime("%Y-%m-%d %H:%M:%S"),
                    'end': None
                    }
        else:
            return {'name': self.name,
                    'matches': serialized_matches,
                    'start': self.start.strftime("%Y-%m-%d %H:%M:%S"),
                    'end': self.end.strftime("%Y-%m-%d %H:%M:%S")
                    }

    @staticmethod
    def deserialize(serialized_instance, player_list):
        name = serialized_instance['name']
        serialized_matches = serialized_instance['matches']
        if 'start' in serialized_instance:
            start = datetime.strptime(serialized_instance['start'],
                                      "%Y-%m-%d %H:%M:%S")
        else:
            start = None
        if serialized_instance['end'] is not None:
            end = datetime.strptime(serialized_instance['end'],
                                    "%Y-%m-%d %H:%M:%S")
        else:
            end = None

        matches = []
        for serialized_match in serialized_matches:
            matches.append(Match.deserialize(serialized_match, player_list))

        return Round(name, matches, start, end)
