from nba_api.live.nba.endpoints import scoreboard
from datetime import datetime, timezone, timedelta
from dateutil import parser
from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.config import Config
from multiprocessing.dummy import Process

Config.set('graphics', 'width', 'auto')
Config.set('graphics', 'height', 'auto')

def on_start(self):
    from kivy import platform
    if platform == "android":
        self.start_service()
    Process(target=self.initiate_load_sequence).start()

def only_print_some(array):
    text = ""
    for i in array.values():
        text += str(i[1])+"   "+str(i[2])+"\n"
    return text

def how_much_time(time1, time2):
    # Parse the input times as datetime objects
    time1 = datetime.strptime(time1, "%H:%M")
    time2 = datetime.strptime(time2, "%H:%M")

    # Handle the case where time2 is on the next day
    if time2 < time1:
        time2 += timedelta(days=1)

    # Calculate the time difference and return it
    return time2 - time1

def remove_last_value(dictionary):
    # Create a new dictionary to hold the modified values
    new_dict = {}

    # Iterate over the key-value pairs in the dictionary
    for key, value in dictionary.items():
        # Create a new list with the last value removed from the original list
        new_list = value[:-1]
        # Add the modified list to the new dictionary
        new_dict[key] = new_list

    # Return the new dictionary
    return new_dict


def print_table(data):
    data = remove_last_value(data)
    text = ""
    headers = ["ID", "TEAMS", "TIME"]
    # Get the length of the longest list in the values of the dictionary
    max_len = max(data) + 1
    # Print the headers
    header_str = ' | '.join(headers)
    text += header_str + "\n"
    text += ('--' * len(header_str))
    # Print the rows of the table
    text += "\n"
    for j in range(int(list(data.keys())[0]), int(max_len)):
        row = []
        for i in range(len(headers)):
            if i < len(data[j]):
                # Right-align values for numeric columns and left-align for other columns
                if headers[i].isdigit():
                    text += (f" {data[j][i]:>{len(headers[i])}}")
                else:
                    text += (f" {data[j][i]:<{len(headers[i])}}")
            else:
                # Pad empty cells with spaces to align with headers
                text += (' ' * len(headers[i]))
        text += (' | '.join(row))
        text += "\n"
    return text


def get_games(half):
    i = 0
    games_today = {}
    board = scoreboard.ScoreBoard()
    games = board.games.get_dict()
    end = len(games)
    for game in games:
        if half == "second":
            if i > int(len(games) * 0.5):
                game_time = str(parser.parse(game["gameTimeUTC"]).replace(tzinfo=timezone.utc).astimezone())[11:16]
                games_today[i] = [i, (game['awayTeam']['teamName'] + " vs " + game['homeTeam']['teamName']), game_time,
                                  game['gameId']]
        else:
            game_time = str(parser.parse(game["gameTimeUTC"]).replace(tzinfo=timezone.utc).astimezone())[11:16]
            games_today[i] = [i, (game['awayTeam']['teamName'] + " vs " + game['homeTeam']['teamName']), game_time,
                              game['gameId']]
            if i > (len(games)) * 0.5 - 1 and half == "first":
                break
        i += 1
    if half == "first" or half == "second":
        return print_table(games_today)
    else:
        return games_today


def new_dict(my_dict, choice):
    print_table(my_dict)
    # Get a list of the keys in the dictionary
    keys = list(my_dict.keys())
    # Get a string of index positions separated by commas from the user
    indices_string = choice
    # Split the string into a list of individual index positions
    index_list = indices_string.split(",")
    # Create a new dictionary with the keys and values from the specified index positions
    new_dict = {keys[int(i)]: my_dict[keys[int(i)]] for i in index_list}
    return new_dict


class MyApp(App):
    def build(self):
        self.time = 0
        # Create a layout to hold the widgets
        self.layout = BoxLayout(orientation='vertical')

        """"# Create a label to display the instructions
        instructions_label = Label(text=get_games(),font_size='10sp')
        layout.add_widget(instructions_label)"""
        self.label_layout = BoxLayout(orientation='horizontal')

        # Create two labels with different text
        self.label1 = Label(text=get_games("first"), font_size='13sp')
        self.label2 = Label(text=get_games("second"), font_size='13sp')
        self.label3 = Label(text="\n\n\n\nPlease enter the game/s I'd/s\n with a comma separator.",
                            font_size='15sp')
        self.label_layout.add_widget(self.label1)
        self.label_layout.add_widget(self.label3)
        self.label_layout.add_widget(self.label2)

        # Add the horizontal layout to the main layout
        self.layout.add_widget(self.label_layout)

        # Create text input widgets for the age, first name, and last name
        self.games_input = TextInput(text="", size_hint=(3, 0.2))
        self.max_time_input = TextInput(text="", size_hint=(3, 0.2))
        self.layout.add_widget(self.games_input)
        self.layout.add_widget(self.max_time_input)
        self.max_time_input.opacity = 0
        # Create a button to submit the form
        self.submit_button = Button(text="Submit", on_release=self.first_submit, size_hint=(0.5, 0.3),
                                    pos_hint={'x': 0.25, 'y': 0.3})
        self.layout.add_widget(self.submit_button)

        # Create a label to display the goodbye message
        self.chosen_games_label = Label(text="")
        self.layout.add_widget(self.chosen_games_label)

        return self.layout

    def first_submit(self, button):
        if self.time == 0:
            # Get the age, first name, and last name from the text input widgets
            self.chosen_games = self.games_input.text
            print(self.chosen_games)
            # Display the goodbye message
            print(get_games("ere"))
            try:
                if not self.chosen_games.replace(",", "").isdigit() and self.chosen_games.replace(",", "") > 0:
                    raise("")
                self.chosen_games_label.text = str(only_print_some(new_dict(get_games("ere"), self.chosen_games)))
            except:
                self.label3.text = "\n\n\n\nPlease enter the game/s I'd/s\n with a comma separator.\nError with input.Go again"
            else:
                self.label1.text = ""
                self.label2.text = ""
                self.label3.text = "Please enter the point difference(in first area).\n And the time left in clock(in second area)."
                self.games_input.text = ""
                self.max_time_input.opacity = 1
                print(self.time)
                self.time += 1
        else:
                self.second_submit()
                self.time += 1

    def second_submit(self):
        print(self.time)
        try:
            if (not (self.games_input.text.isdigit()) and int(self.games_input.text > 0) or (not (self.max_time_input.text.isdigit()) and int(self.self.max_time_input.text > 0))):
                    raise("")
            self.max_score = int(self.games_input.text)
            self.max_time = int(self.max_time_input.text)
        except:
            self.label3.text = "Please enter the point difference(in first area).\n And the time left in clock(in second area).\nError with input,go again"
        else:
            self.layout.remove_widget(self.submit_button)
            self.layout.remove_widget(self.games_input)
            self.layout.remove_widget(self.max_time_input)
            self.wait_to_the_games(new_dict(get_games("ere"), self.chosen_games))

    @staticmethod
    def start_service():
        from jnius import autoclass
        service = autoclass("org.test.nbaBGBeta.ServiceBack_ground")
        mActivity = autoclass("org.kivy.android.PythonActivity").mActivity
        service.start(mActivity, "")
        return service

if __name__ == "__main__":
    MyApp().run()