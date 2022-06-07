from abc import ABC, abstractmethod


class AbstractView(ABC):
    """
    This abstract class define all mandatory methods to display listing
    and menu needed by the tournament manager controller

    :parameter
        controller : the tournament manager Controller
    """

    @abstractmethod
    def display_highest_level_menu(self, highest_level_commands):
        """highest level menu, must be available at any time

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
        """display a simple list of items"""
        pass

    @abstractmethod
    def display_table(self, description: str, dict_list: list):
        """display a table, with description and headers

        :param description: a string to display to introduce table
        :param dict_list: a list of dict, keys will be used as headers of table
        """
        pass

    @abstractmethod
    def display_form(self, needed_infos: tuple, return_function):
        """Method to display a form
        and return results to a function in parameter
        :param needed_infos: a tuple of dict as
                                    'label': a string to display
                                    'type' : indicates what should be returned
        :param return_function:
               the function where to send the list of needed datas
        """
        pass

    @abstractmethod
    def log(self, message: str):
        """a simple display message function"""
        pass
