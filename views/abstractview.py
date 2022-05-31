from abc import ABC, abstractmethod


class AbstractView(ABC):
    """
    This abstract class need all mandatory methods to display listing and menu
    needed by the tournament manager controller

    :parameter
        controller : the tournament manager Controller
    """

    @abstractmethod
    def display_highest_level_menu(self, highest_level_commands):
        """display highest level menu, must be available at any time
        :param highest_level_commands: is a list of dict like:
            {'short': "s", ->shortcut
             'long': "sauvegarder", ->a word (maybe to display on a button)
             'label': "pour sauvegarder les données en cours d'utilisation",
             ->a full sentence (for a tooltip for instance)
             'function': self.save -> a callback function
             },
        """
        pass

    @abstractmethod
    def display_menu(self, title, options_list, action_list):
        """display a normal menu. each option refer to an action
            :param title a string
            :param options_list is a string list
            :param action_list is a callback functions list
                both lists must be same length
        """
        pass

    @abstractmethod
    def display_item_choice(self, title, options_list, return_function):
        """display a item choice menu.
            the return_function will accept one of the options in arg
                :param title a string
                :param options_list is a 'stringable' object list
                :param return_function is a callback function
                        which will receive one object of the list in arg
        """
        pass

    @abstractmethod
    def display_list(self, item_list):
        pass

    @abstractmethod
    def display_table(self, dict_list):
        pass

    @abstractmethod
    def display_form(self, needed_infos: tuple, return_function):
        """Method to display a form
        and return results to a function in parameter"""
        pass

    @abstractmethod
    def log(self, message: str):
        pass
