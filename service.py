from jnius import autoclass
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from nba_api.live.nba.endpoints import scoreboard
from datetime import datetime, timedelta

PythonService = autoclass('org.kivy.android.PythonService')
PythonService.mService.setAutoRestartService(True)


while True:
    try:
        def how_much_time(time1, time2):
            # Parse the input times as datetime objects
            time1 = datetime.strptime(time1, "%H:%M")
            time2 = datetime.strptime(time2, "%H:%M")

            # Handle the case where time2 is on the next day
            if time2 < time1:
                time2 += timedelta(days=1)

            # Calculate the time difference and return it
            return time2 - time1

        def wait_to_the_games(self, games_today):
            self.chosen_games_label.text += f"\nchosen time:{self.max_time_input.text}       chosen points:{self.games_input.text}"
            self.games_today = games_today
            self.label3.text = "wait for the games to began"
            this_hour = str(datetime.now())[11:16]
            dict_keys = list(games_today.keys())
            v = games_today[dict_keys[0]][2]
            is_time_right = how_much_time(this_hour, games_today[dict_keys[0]][2])
            print(is_time_right)
            is_time_right = str(is_time_right).split(":")
            is_time_right = int(is_time_right[0]) * 60 + int(is_time_right[1])
            if is_time_right > 720:
                Clock.schedule_once(self.game, 1)
            else:
                Clock.schedule_once(self.game, int(60 * is_time_right))

        def game(self, some):
            board = scoreboard.ScoreBoard()
            games = board.get_dict()
            text = ""
            print("ScoreBoardDate: " + board.score_board_date)
            games_wanted = self.games_today
            for i in range(len(games["scoreboard"]["games"])):
                if games["scoreboard"]["games"][i]["gameStatusText"][1:2].isnumeric() and games["scoreboard"]["games"][i][
                                                                                              "gameStatusText"][
                                                                                          6:7].isnumeric():
                    for ii in range(len(list(games_wanted.values()))):
                        if games["scoreboard"]["games"][i]["gameId"] == list(games_wanted.values())[ii][3]:
                            game_time = int(games["scoreboard"]["games"][i]["gameStatusText"][1:2]) * 12 - 12 + int(
                                games["scoreboard"]["games"][i]["gameStatusText"][3:5])
                            score1 = int(games["scoreboard"]["games"][i]["homeTeam"]["score"])
                            score2 = int(games["scoreboard"]["games"][i]["awayTeam"]["score"])
                            text += str(games["scoreboard"]["games"][i]["gameStatusText"]) + "\n"
                            text += str(str(games["scoreboard"]["games"][i]["homeTeam"]["teamName"]) + "-" + str(
                                score1) + ":" + str(score2) + "-" + str(
                                games["scoreboard"]["games"][i]["awayTeam"]["teamName"]))
                            is_score_good2 = score1 - score2 <= self.max_score and score1 - score2 >= 0
                            is_score_good = score2 - score1 <= self.max_score and score2 - score1 >= 0
                            if list(games_wanted.values())[ii][0] != 100 and (is_score_good or is_score_good2) and (
                                    self.max_time + game_time) > 48:
                                list(games_wanted.values())[ii][0] = 100
                                sound = SoundLoader.load('ffd.mp3')
                                if sound:
                                    sound.play()
    except:
        pass
        
       

        self.label3.text = text
        Clock.schedule_once(self.game, 10)
