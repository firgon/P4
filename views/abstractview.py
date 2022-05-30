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
        pass

    @abstractmethod
    def display_menu(self, title, options_list, action_list):
        pass

    @abstractmethod
    def display_item_choice(self, title, options_list, return_function):
        pass

    @abstractmethod
    def display_list(self, item_list):
        pass

    @abstractmethod
    def display_form(self, needed_infos: tuple, return_function):
        """Method to display a form
        and return results to a function in paramenter"""
        pass

    @abstractmethod
    def log(self, message: str):
        pass
