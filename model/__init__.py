from abc import ABC, abstractmethod


class Serializable(ABC):
    """This abstract class provides 2 abstracts method
        to serialize and deserialize objects of the model
        in Tournament Manager Project
    """

    @abstractmethod
    def serialize(self):
        """This method return a serialized instance of the object
                ::return a dict of string"""
        pass

    @staticmethod
    @abstractmethod
    def deserialize(serialized_instance, players_by_id: dict = None):
        """This method receive a dict of string and create a new instance

                ::param serialized_instance (a dict of string)
                ::param player_list to pick players instances
                        (using id_in_db attributes)
                        instead of recreate them
                ::return a new instance of the object"""
        pass
