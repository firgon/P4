from views.abstractview import AbstractView
from datetime import date, datetime


class ConsoleView(AbstractView):
    """A view class to display the Tournament Manager in a console
    It creates meta-commands available on each input to quit/save/load
    """

    def __init__(self):
        for i in range(5):
            print()

        print("Manager de Tournoi d'échecs")

        self.meta_commands = dict()

    def display_highest_level_menu(self, list_commands):
        for command in list_commands:
            shortcut = command['short'].upper()
            self.meta_commands["/" + str(shortcut)] = \
                {'label': command['label'],
                 'function': command['function']}

        self.meta_commands["/HELP"] = \
            {'label': "pour revoir les commandes magiques",
             'function': self.prompt_help}

        self.prompt_help()

    def decorator_factory(self):
        def deco(function):
            def wrapper(*args, **kwargs):
                print()
                print("**********************************************")
                answer = function(*args, **kwargs)
                if not self.check_meta_commands(answer):
                    return answer

            return wrapper
        return deco

    def display_menu(self, title, options_list, action_list):
        print()
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
        else:
            for index, item in enumerate(item_list):
                print(str(index) + ": " + str(item))

    def display_table(self, description, dict_list):
        """method to display as a table a list of dict given in parameter"""
        print(description)

        if not dict_list:
            print("Rien à Afficher\n")
            return

        # table can't be less width than 50 chars
        min_width = 50
        keys = dict_list[0].keys()
        nb_column = len(keys)

        # search for the max length of each column
        max_widths = dict()
        for key in keys:
            max_widths[key] = self.get_max_width(key, dict_list)

        # then calculate the new minimum width of the table
        width_sum = 0
        for width in max_widths.values():
            width_sum += int(width)

        # if width sum is lower than min width give extra width to each column
        width_more = round(max(0, (min_width - width_sum))/nb_column)

        widths = dict()
        for key in keys:
            widths[key] = max_widths[key] + width_more

        # print keys line
        for key in keys:
            unused_width = widths[key] - len(key)
            # fill unused width with - (header)
            print("- " + key + " "
                  + self.get_variable_length_string(unused_width, "-"),
                  end='')

        print()

        for obj in dict_list:
            for key in keys:
                unused_width = widths[key] - len(str(obj[key]))
                # fill unused width with " " (normal line)
                print("|  " + str(obj[key]) +
                      self.get_variable_length_string(unused_width),
                      end='')
            print("|")

        # fill all column with "-" (table bottom)
        for key in keys:
            print(self.get_variable_length_string(widths[key]+3, "-"),
                  end='')

        print("\n")

    def prompt_choice(self, options_list, question="Quel est votre choix ?")\
            -> int:
        """ Method to display options in the console
        and return a int corresponding to the choice

        :param options_list : list of string option
        :param question: (optional) question of the input

        :return int corresponding to the chosen option in list
        """
        print(question)

        self.display_list(options_list)

        answer = input("Tapez votre réponse: ")
        print()

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
            return self.prompt_choice(options_list, question)

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
            elif info['type'] == date:
                collected_infos.append(self.ask_for_date(info['label']))
            elif info['type'] == list[date]:
                collected_infos.append(self.ask_for_date_list(info['label']))
            else:
                collected_infos.append(info['type'])

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
        print()
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

        while True:
            num_value = len(values)+1
            new_date = self.ask_for_date("(" + str(num_value) + ") " + label)

            if new_date == '':
                if num_value > 1:
                    break
                else:
                    continue
            else:
                values.append(new_date)

        return values

    def ask_for_date(self, label: str):
        print("Écrivez la date au format JJ/MM/AA")

        value = input(label + " : ")
        print()

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
