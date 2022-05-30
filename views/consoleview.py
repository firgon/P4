from views.abstractview import AbstractView
from datetime import date, datetime
from Model.player import Player
from Model.tournament import Tournament


class ConsoleView(AbstractView):
    """A view class to display the Tournament Manager in a console
    It creates meta-commands available on each input to quit/save/load
    """

    def __init__(self):
        for i in range(5):
            print()

        print("Manager de Tournoi d'échecs")

        self.meta_commands = None

    def display_highest_level_menu(self, list_commands):
        self.meta_commands = dict()
        for command in list_commands:
            shortcut = command['short'].upper()
            self.meta_commands["/" + str(shortcut)] = \
                {'label': command['label'],
                 'function': command['function']}

        self.meta_commands["/HELP"] = \
            {'label': "pour revoir les commandes magiques",
             'function': self.prompt_help}

        self.prompt_help()

    def decorated(self, function):

        def wrapper(*args, **kwargs):
            answer = function(*args, **kwargs)
            if not self.check_meta_commands(answer):
                return answer

        return wrapper()

    def display_menu(self, title, options_list, action_list):
        print("**********************************************")
        print(title)
        self.prompt_action_choice(options_list, action_list)

    def display_item_choice(self, title, options_list, return_function):
        """display a list of options and return chosen element"""
        choice = self.prompt_choice(options_list, title)
        return_function(options_list[choice])

    def display_list(self, item_list):
        """display a list received in parameter
        with index : value if it is a simple list
        as a table if it is a list of dict"""
        if len(item_list) == 0:
            print("La liste est vide, tapez /EXIT pour sortir de là.")
        elif isinstance(item_list[0], dict):
            self.display_table(item_list)
        else:
            for index, item in enumerate(item_list):
                print(str(index) + ": " + str(item_list[index]))

    def display_table(self, dict_list):
        """method to display as a table a list of dict given in parameter"""
        min_width = 50
        keys = dict_list[0].keys()
        nb_column = len(keys)

        max_widths = dict()
        for key in keys:
            max_widths[key] = self.get_max_width(key, dict_list)

        width_sum = 0
        for width in max_widths.values():
            width_sum += int(width)

        width_more = round((min_width - width_sum)/nb_column)

        widths = dict()
        for key in keys:
            widths[key] = max_widths[key] + width_more

        # print keys line
        for key in keys:
            unused_width = widths[key] - len(key)
            print("- " + key + " "
                  + self.get_variable_length_string(unused_width, "-"),
                  end='')

        print()

        for obj in dict_list:
            for key in keys:
                unused_width = widths[key] - len(str(obj[key]))
                print("|  " + str(obj[key]) +
                      self.get_variable_length_string(unused_width),
                      end='')
            print("|")

        for key in keys:
            print(self.get_variable_length_string(widths[key]+3, "-"),
                  end='')

        print()

    def prompt_choice(self, options_list, question="Quel est votre choix ?"):
        """ Method to display options in the console
        and return a int corresponding to the choice

        :param options_list : list of string option
        :param question: (optional) question of the input
        """
        print(question)

        self.display_list(options_list)

        answer = input("Tapez votre réponse: ")

        if not self.check_meta_commands(answer):
            try:
                int_answer = int(answer)
                if int_answer not in range(len(options_list)):
                    raise SyntaxError()
                else:
                    return int_answer
            except (ValueError, SyntaxError):
                print(f"'{answer}' n'est pas une réponse valide")
                print("Les réponses valides sont :", end=" ")
                print(*range(len(options_list)), sep=', ')
                return self.prompt_choice(options_list, question)

        else:
            self.act_meta_commands(answer)

    def prompt_action_choice(self,
                             options_list,
                             return_function_list,
                             question="Que souhaitez-vous faire ?"):
        """Method to display options in the console
        and launch method according to the user answer

        :param options_list: list of string option
        :param return_function_list:
                function of the Controller to launch with input in arg
        :param question: (optional) question of the input
        """
        answer = self.prompt_choice(options_list, question)
        return_function_list[answer]()

    def prompt_help(self):
        """this method display options available on each input
         save/load/input"""
        print("**** IMPORTANT ****")
        print("A n'importe quel moment, "
              "vous pouvez utiliser les commandes magiques :")
        for key in self.meta_commands:
            print(key + ": " + self.meta_commands[key]['label'])

        print("****")

    def check_meta_commands(self, answer):
        """This method checks if a meta command has been used in a answer given
        in any input of the app

        :param answer: string received by an input
        :return: false if no meta command have been detected
        """

        if answer in self.meta_commands:
            return True
        else:
            return False

    def act_meta_commands(self, answer):
        self.meta_commands[answer]['function']()

    def display_form(self, needed_infos: tuple, return_function):
        """this method collect datas from user
        and send them to a return function

        :param needed_infos: a tuple of dict as (label, data type)
        :param return_function:
               the retour function where to send the list of needed datas
         """

        collected_infos = []
        for info in needed_infos:
            if info['type'] == str:
                collected_infos.append(self.ask_for_str(info['label']))
            elif info['type'] == int:
                collected_infos.append(self.ask_for_int(info['label']))
            elif isinstance(info['type'], int):
                collected_infos.append(self.ask_for_int(info['label'],
                                                        info['type']))
            elif isinstance(info['type'], str):
                collected_infos.append(self.ask_for_str(info['label'],
                                                        info['type']))
            elif isinstance(info['type'], tuple):
                choice = self.prompt_choice(info['type'], info['label'])
                collected_infos.append(choice)
            elif isinstance(info['type'], Player) \
                    or isinstance(info['type'], Tournament):
                collected_infos.append(info['type'])
            elif info['type'] == date:
                collected_infos.append(self.ask_for_date(info['label']))
            elif info['type'] == list[date]:
                collected_infos.append(self.ask_for_date_list(info['label']))

        return_function(collected_infos)

    @staticmethod
    def ask_for_str(label: str, default=None):
        """Method to display a input to collect a string value"""
        if default is not None:
            value = input(label
                          + " (ENTREE pour confirmer "
                            "la valeur par défaut qui est : "
                          + str(default) + " ) : ")
            if value == '':
                value = default
        else:
            value = input(label + " : ")
        return value

    def ask_for_int(self, label: str, default=None):
        """Same as ask_for_str but accepts only int values"""

        value = self.ask_for_str(label, default)

        try:
            retour = int(value)
            return retour
        except ValueError:
            print("Veuillez rentrer un nombre")
            return self.ask_for_int(value, default)

    def ask_for_date_list(self, label: str):
        values = []
        print("Plusieurs valeurs peuvent être renseignées\n"
              "tapez simplement ENTREE pour finir")

        index = 1
        while True:
            new_date = self.ask_for_date("(" + str(index) + ") " + label)

            if new_date == '':
                break
            else:
                values.append(new_date)
                index += 1

        return values

    def ask_for_date(self, label: str):
        print("Écrivez la date au format JJ/MM/AA")

        value = input(label + " : ")

        if value == '':
            return value

        try:
            # check that format is DD/MM/YY and return a formatted string
            new_date = datetime.strptime(value, '%d/%m/%y')
            return new_date
        except ValueError:
            print("Le format n'est pas le bon")
            return self.ask_for_date(label)

    def log(self, message: str):
        print(message)

    @staticmethod
    def get_variable_length_string(length: int, string=" "):
        """return a string of needed length, full with string parameter"""

        result = string

        for i in range(length):
            result += string

        return result

    @staticmethod
    def get_max_width(key, item_list):
        """This function return the max length of values in a list of dict

        :param key the key to be checked on each object
        :param item_list the list of object
        """
        max_value = len(key)
        for item in item_list:
            max_value = max(max_value, len(str(item[key])))

        return max_value