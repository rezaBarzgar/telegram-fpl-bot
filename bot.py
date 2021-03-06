import datetime

import requests
import telegram
from telegram.ext import Updater, CommandHandler
from telegram.ext import MessageHandler, Filters
import logging
import statistics
import utils
import pandas as pd
import os

#  -------------------- START ------------------------------------
sts = statistics.Statistics()
teams_dict = sts.get_teams()
for key, value in teams_dict.items():
    teams_dict[key] = value.lower()
CURRENT_GW = sts.get_current_gw()
TEAMS_TO_STRING = ''
SPLITTER = 30 * '~'
CHANNEL_AND_BOT_ID = '@FPL_TALK\n@FPL_TALK_BOT'
STATS = None
DEADLINE = None
LAST_STATS_UPDATE = datetime.datetime.now()
TOKEN = os.environ["TOKEN"]
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
job_queue = updater.job_queue


#  -------------------- FUNCTIONS --------------------------------
def stats_updater(update='', context=''):
    try:
        global STATS
        global DEADLINE
        global CURRENT_GW
        CURRENT_GW = sts.get_current_gw()
        STATS = pd.DataFrame(sts.update_statistics())
        STATS['name'] = STATS['first_name'] + ' ' + STATS['second_name'] + ' ' + STATS['web_name']
        DEADLINE = sts.update_deadline()
        STATS['dreamteam_count'] = pd.to_numeric(STATS['dreamteam_count'])
        STATS['ep_next'] = pd.to_numeric(STATS['ep_next'])
        STATS['ep_this'] = pd.to_numeric(STATS['ep_this'])
        STATS['event_points'] = pd.to_numeric(STATS['event_points'])
        STATS['form'] = pd.to_numeric(STATS['form'])
        STATS['now_cost'] = pd.to_numeric(STATS['now_cost'])
        STATS['points_per_game'] = pd.to_numeric(STATS['points_per_game'])
        STATS['transfers_in_event'] = pd.to_numeric(STATS['transfers_in_event'])
        STATS['transfers_out_event'] = pd.to_numeric(STATS['transfers_out_event'])
        STATS['minutes'] = pd.to_numeric(STATS['minutes'])
        STATS['goals_scored'] = pd.to_numeric(STATS['goals_scored'])
        STATS['assists'] = pd.to_numeric(STATS['assists'])
        STATS['clean_sheets'] = pd.to_numeric(STATS['clean_sheets'])
        STATS['goals_conceded'] = pd.to_numeric(STATS['goals_conceded'])
        STATS['own_goals'] = pd.to_numeric(STATS['own_goals'])
        STATS['penalties_saved'] = pd.to_numeric(STATS['penalties_saved'])
        STATS['penalties_missed'] = pd.to_numeric(STATS['penalties_missed'])
        STATS['yellow_cards'] = pd.to_numeric(STATS['yellow_cards'])
        STATS['red_cards'] = pd.to_numeric(STATS['red_cards'])
        STATS['saves'] = pd.to_numeric(STATS['saves'])
        STATS['bonus'] = pd.to_numeric(STATS['bonus'])
        STATS['ict_index'] = pd.to_numeric(STATS['ict_index'])
        STATS['ict_index_rank'] = pd.to_numeric(STATS['ict_index_rank'])
        global LAST_STATS_UPDATE
        LAST_STATS_UPDATE = datetime.datetime.now()
    except ConnectionError:
        print(f"unable to get data from premier league api at {datetime.datetime.now()}")


def teams_to_string():
    global TEAMS_TO_STRING
    for key, value in teams_dict.items():
        TEAMS_TO_STRING += f"{value.lower()}\n"


job_queue.run_repeating(callback=stats_updater, interval=1800, first=5.0)


def hello(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="I'm FPL bot, talk to me!\nI recommend you to see /help")


def help(update, context):
    message = """?????????????? ?????????????? ???? ???????? Persian FPL Talk.
??????????: /player
??????????: ?????? ???????????? ???? ?????????????? ???? ???????? ????????
??????????: ?????????????? ????????????
????????: 
/player salah
------------------------------------
??????????: /compare
??????????: ?????? ???????????? ???? ???? ?????????????? ???? ???? (-) ???? ???? ?????? ?????? ??????.
??????????: ???????????? ????????????????
????????: 
/compare mount - havertz
------------------------------------
??????????: /popular_players 
??????????: ?????????? ???????????????? ?????????? (??????????????)
??????????: ?????????????? ???????????????? ?????????? ???? ???????? ???????? ????????????
????????:
/popular_players 10
------------------------------------
?????????? ?????? /popular_forwards?? /popular_midfielders?? /popular_defenders ?? /popular_goalkeepers ?????? ?????????? ?????????? ???????? ?????? ???????????? ???????? ?????? ?????? ??????????.
------------------------------------
??????????: /onfire_players 
??????????: ?????????? ???????????????? ?????? ?????? (??????????????)
??????????: ?????????????? ???????????????? ?????? ??????
????????:
/onfire_players 10
------------------------------------
?????????? ?????? /onfire_forwards?? /onfire_midfielders?? /onfire_defenders ?? /onfire_goalkeepers ?????? ?????????? ?????????? ???????? ?????? ???????????? ???????? ?????? ?????? ??????????.
------------------------------------
??????????: /next_games
??????????: ?????? ??????
??????????: ???????? ?????? ???????? ?????? ???????? ??????
????????:
/next_games man utd
------------------------------------
??????????: /easy_games
??????????: ?????????? ?????? ?????? ???????? ?????? (??????????????)
??????????: ???????? 5 ???????? ???????? ?????? ???? ???? ???? ???????? ?????????? ???????? ??????
????????:
/easy_games 6
------------------------------------
??????????: /hard_games
??????????: ?????????? ?????? ?????? ???????? ?????? (??????????????)
??????????: ???????? 5 ???????? ???????? ?????? ???? ???? ???? ???????? ???????? ???????? ??????
????????:
/hard_games 6
------------------------------------
??????????: /flip_coin
??????????: ?????? ???? ???????????? ???? ???? (-) ???? ???? ?????? ?????? ??????
??????????: ?????? ?????? ???? ???????????????? ??????????
????????:
/flip_coin salah - fernandes
------------------------------------
??????????: /deadline
??????????: ??????????
??????????: ?????????? ?????????? ???? ???????????? ?? ????????
????????:
/deadline
------------------------------------
@FPL_TALK
@FPL_TALK_BOT
"""
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)


def deadline(update, context):
    message = DEADLINE + CHANNEL_AND_BOT_ID
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)


def player_stats(update, context):
    # TODO User freindly nist
    player_name = '.*?'.join(context.args)
    player_name = utils.strip_accents(player_name).lower()
    player_name = '.*?' + player_name + '.*?'
    data = STATS[STATS.name.str.contains(player_name, regex=True)].reset_index()
    response_message = ""
    if data.shape[0] == 0:
        response_message = "sorry, I cannot find player with this name :( \n" + CHANNEL_AND_BOT_ID
    elif data.shape[0] >= 2:
        response_message = "MORE THAN 1 PLAYER FOUND!\n" + SPLITTER + '\n'
        for index, row in data.iterrows():
            temp = f"first name: {row.first_name}\n" \
                   f"last name : {row.second_name}\n" \
                   f"cost : {row.now_cost / 10}\n" \
                   f"form : {row.form}\n" \
                   f"ict_index_rank : {row.ict_index_rank}\n" + \
                   f"{row.team.lower()} next games: " + sts.get_next_games_color(row.team.lower())
            response_message = response_message + temp + SPLITTER + '\n'
        response_message = response_message + CHANNEL_AND_BOT_ID
    elif data.shape[0] == 1:
        response_message = f"first name: {data.first_name.item()}\n" \
                           f"last name : {data.second_name.item()}\n" \
                           f"cost : {data.now_cost.item() / 10}\n" \
                           f"form : {data.form.item()}\n" \
                           f"total points : {data.total_points.item()}\n" \
                           f"points per game : {data.points_per_game.item()}\n" \
                           f"ict_index_rank : {data.ict_index_rank.item()}\n" \
                           f"{data.team.item().lower()} next games: " + sts.get_next_games_color(
            data.team.item().lower()) + '\n' + CHANNEL_AND_BOT_ID

    context.bot.send_message(chat_id=update.effective_chat.id, text=response_message)


def popular_players(update, context):
    if len(context.args) == 0:
        count = 5
    else:
        count = int(''.join(context.args))
    df = STATS.sort_values(by=['selected_by_percent'], ascending=False).head(count).reset_index()
    response_message = ""
    for index, row in df.iterrows():
        temp = f"player {index + 1}: {row.web_name}   selected: {row.selected_by_percent}   cost: {int(row.now_cost) / 10}   " \
               f"position: {row.element_type}   team: {row.team}\n"
        response_message = response_message + temp + SPLITTER + '\n'
    response_message = response_message + CHANNEL_AND_BOT_ID
    context.bot.send_message(chat_id=update.effective_chat.id, text=response_message)


def popular_forwards(update, context):
    if len(context.args) == 0:
        count = 5
    else:
        count = int(''.join(context.args))
    df = STATS.sort_values(by=['selected_by_percent'], ascending=False)
    df = df[df.element_type == 'Forward'].head(count).reset_index()
    response_message = ""
    for index, row in df.iterrows():
        temp = f"player {index + 1}: {row.web_name}   selected: {row.selected_by_percent}   cost: {int(row.now_cost) / 10}   " \
               f"team: {row.team}\n"
        response_message = response_message + temp + SPLITTER + '\n'
    response_message = response_message + CHANNEL_AND_BOT_ID
    context.bot.send_message(chat_id=update.effective_chat.id, text=response_message)


def popular_midfielders(update, context):
    if len(context.args) == 0:
        count = 5
    else:
        count = int(''.join(context.args))

    df = STATS.sort_values(by=['selected_by_percent'], ascending=False)
    df = df[df.element_type == 'Midfielder'].head(count).reset_index()
    response_message = ""
    for index, row in df.iterrows():
        temp = f"player {index + 1}: {row.web_name}   selected: {row.selected_by_percent}   cost: {int(row.now_cost) / 10}   " \
               f"team: {row.team}\n"
        response_message = response_message + temp + SPLITTER + '\n'
    response_message = response_message + CHANNEL_AND_BOT_ID
    context.bot.send_message(chat_id=update.effective_chat.id, text=response_message)


def popular_defenders(update, context):
    if len(context.args) == 0:
        count = 5
    else:
        count = int(''.join(context.args))

    df = STATS.sort_values(by=['selected_by_percent'], ascending=False)
    df = df[df.element_type == 'Defender'].head(count).reset_index()
    response_message = ""
    for index, row in df.iterrows():
        temp = f"player {index + 1}: {row.web_name}   selected: {row.selected_by_percent}   cost: {int(row.now_cost) / 10}   " \
               f"team: {row.team}\n"
        response_message = response_message + temp + SPLITTER + '\n'
    response_message = response_message + CHANNEL_AND_BOT_ID
    context.bot.send_message(chat_id=update.effective_chat.id, text=response_message)


def popular_goalkeepers(update, context):
    if len(context.args) == 0:
        count = 5
    else:
        count = int(''.join(context.args))

    df = STATS.sort_values(by=['selected_by_percent'], ascending=False)
    df = df[df.element_type == 'Goalkeeper'].head(count).reset_index()
    response_message = ""
    for index, row in df.iterrows():
        temp = f"player {index + 1}: {row.web_name}   selected: {row.selected_by_percent}   cost: {int(row.now_cost) / 10}   " \
               f"team: {row.team}\n"
        response_message = response_message + temp + SPLITTER + '\n'
    response_message = response_message + CHANNEL_AND_BOT_ID
    context.bot.send_message(chat_id=update.effective_chat.id, text=response_message)


def onfire_players(update, context):
    if len(context.args) == 0:
        count = 5
    else:
        count = int(''.join(context.args))
    df = STATS.sort_values(by=['form'], ascending=False).head(count).reset_index()
    response_message = ""
    for index, row in df.iterrows():
        temp = f"player {index + 1}: {row.web_name}   selected: {row.selected_by_percent}   cost: {int(row.now_cost) / 10}   " \
               f"position: {row.element_type}   team: {row.team}\n"
        response_message = response_message + temp + SPLITTER + '\n'
    response_message = response_message + CHANNEL_AND_BOT_ID
    context.bot.send_message(chat_id=update.effective_chat.id, text=response_message)


def onfire_forwards(update, context):
    if len(context.args) == 0:
        count = 5
    else:
        count = int(''.join(context.args))
    df = STATS.sort_values(by=['form'], ascending=False)
    df = df[df.element_type == 'Forward'].head(count).reset_index()
    response_message = ""
    for index, row in df.iterrows():
        temp = f"player {index + 1}: {row.web_name}   selected: {row.selected_by_percent}   cost: {int(row.now_cost) / 10}   " \
               f"team: {row.team}\n"
        response_message = response_message + temp + SPLITTER + '\n'
    response_message = response_message + CHANNEL_AND_BOT_ID
    context.bot.send_message(chat_id=update.effective_chat.id, text=response_message)


def onfire_midfielders(update, context):
    if len(context.args) == 0:
        count = 5
    else:
        count = int(''.join(context.args))

    df = STATS.sort_values(by=['form'], ascending=False)
    df = df[df.element_type == 'Midfielder'].head(count).reset_index()
    response_message = ""
    for index, row in df.iterrows():
        temp = f"player {index + 1}: {row.web_name}   selected: {row.selected_by_percent}   cost: {int(row.now_cost) / 10}   " \
               f"team: {row.team}\n"
        response_message = response_message + temp + SPLITTER + '\n'
    response_message = response_message + CHANNEL_AND_BOT_ID
    context.bot.send_message(chat_id=update.effective_chat.id, text=response_message)


def onfire_defenders(update, context):
    if len(context.args) == 0:
        count = 5
    else:
        count = int(''.join(context.args))

    df = STATS.sort_values(by=['form'], ascending=False)
    df = df[df.element_type == 'Defender'].head(count).reset_index()
    response_message = ""
    for index, row in df.iterrows():
        temp = f"player {index + 1}: {row.web_name}   selected: {row.selected_by_percent}   cost: {int(row.now_cost) / 10}   " \
               f"team: {row.team}\n"
        response_message = response_message + temp + SPLITTER + '\n'
    response_message = response_message + CHANNEL_AND_BOT_ID
    context.bot.send_message(chat_id=update.effective_chat.id, text=response_message)


def onfire_goalkeepers(update, context):
    if len(context.args) == 0:
        count = 5
    else:
        count = int(''.join(context.args))

    df = STATS.sort_values(by=['form'], ascending=False)
    df = df[df.element_type == 'Goalkeeper'].head(count).reset_index()
    response_message = ""
    for index, row in df.iterrows():
        temp = f"player {index + 1}: {row.web_name}   selected: {row.selected_by_percent}   cost: {int(row.now_cost) / 10}   " \
               f"team: {row.team}\n"
        response_message = response_message + temp + SPLITTER + '\n'
    response_message = response_message + CHANNEL_AND_BOT_ID
    context.bot.send_message(chat_id=update.effective_chat.id, text=response_message)


def next_games(update, context):
    if TEAMS_TO_STRING == '':
        teams_to_string()
    team = ' '.join(context.args)
    if team in teams_dict.values():
        response = f"{team} next games:\n" + SPLITTER + "\n" + sts.get_next_games(
            team) + CHANNEL_AND_BOT_ID
    else:
        response = 'your input must be one of the following names:\n' + TEAMS_TO_STRING + \
                   CHANNEL_AND_BOT_ID
    context.bot.send_message(chat_id=update.effective_chat.id, text=response)


def easy_matches(update, context):
    if len(context.args) == 0:
        count = 5
    else:
        count = int(''.join(context.args))
    if not 1 <= count <= 20:
        response = "wrong input!\nInput must be in a number between 1 and 20."
        context.bot.send_message(chat_id=update.effective_chat.id, text=response)
        return
    difficulties = pd.DataFrame(sts.calculate_difficulties())
    difficulties.columns = ['team', 'difficulty']
    difficulties = difficulties.sort_values(by=['difficulty']).head(count).reset_index()
    response = ""
    for index, row in difficulties.iterrows():
        response += f"{row.team} difficulty: {row.difficulty}\n\n" \
                    f"{sts.get_next_games(row.team)}\n" + SPLITTER + '\n'
    response += CHANNEL_AND_BOT_ID
    context.bot.send_message(chat_id=update.effective_chat.id, text=response)


def hard_matches(update, context):
    if len(context.args) == 0:
        count = 5
    else:
        count = int(''.join(context.args))
    if not 1 <= count <= 20:
        response = "wrong input!\nInput must be in a number between 1 and 20."
        context.bot.send_message(chat_id=update.effective_chat.id, text=response)
        return
    difficulties = pd.DataFrame(sts.calculate_difficulties())
    difficulties.columns = ['team', 'difficulty']
    difficulties = difficulties.sort_values(by=['difficulty'], ascending=False).head(count).reset_index()
    response = ""
    for index, row in difficulties.iterrows():
        response += f"{row.team} difficulty: {row.difficulty}\n\n" \
                    f"{sts.get_next_games(row.team)}\n" + SPLITTER + '\n'
    response += CHANNEL_AND_BOT_ID
    context.bot.send_message(chat_id=update.effective_chat.id, text=response)


def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


def coin_flip(update, context):
    try:
        player1, player2 = ' '.join(context.args).split('-')
        message = "coin flip result: " + sts.coin_flip(player1, player2) + '\n' + CHANNEL_AND_BOT_ID
    except Exception as e:
        message = "Invalid input:(\ntwo players must be divided by (-)\nFor example salah - fernandes\n" \
                  + CHANNEL_AND_BOT_ID
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)


def compare(update, context):
    try:
        playerA, playerB = ' '.join(context.args).split('-')
        playerA = playerA.strip()
        playerB = playerB.strip()
        print('-' + playerA + '-')
        print('-' + playerB + '-')
    except Exception as e:
        message = "Invalid input:(\ntwo players must be divided by (-)\nFor example salah - fernandes\n" \
                  + CHANNEL_AND_BOT_ID
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        return
    try:
        playerA = '.*?' + playerA.replace(' ', '.*?') + '.*?'
        playerB = '.*?' + playerB.replace(' ', '.*?') + '.*?'
        player1 = STATS[STATS.name.str.contains(playerA)].iloc[0]
        player2 = STATS[STATS.name.str.contains(playerB)].iloc[0]
    except Exception as e:
        message = "Unable to find one or two players, maybe there is a typo in inputs.\n" \
                  + CHANNEL_AND_BOT_ID
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        return
    player1_score = 0
    player2_score = 0
    diff_dict = dict(sts.calculate_difficulties())
    message = ""
    if float(player1.form) > float(player2.form):
        message += f"Form: {player1.first_name} {player1.web_name}\n"
        player1_score += 5
    elif float(player2.form) > float(player1.form):
        message += f"Form: {player2.first_name} {player2.web_name}\n"
        player2_score += 5
    else:
        message += "Form: equal\n"

    if player1.goals_scored > player2.goals_scored:
        message += f"Goals: {player1.first_name} {player1.web_name}\n"
        player1_score += (player1.goals_scored - player2.goals_scored)
    elif player2.goals_scored > player1.goals_scored:
        message += f"Goals: {player2.first_name} {player2.web_name}\n"
        player2_score += (player2.goals_scored - player1.goals_scored)
    else:
        message += "Goals: equal\n"

    if player1.assists > player2.assists:
        message += f"Assists: {player1.first_name} {player1.web_name}\n"
        player1_score += (player1.assists - player2.assists)
    elif player2.assists > player1.assists:
        message += f"Assists: {player2.first_name} {player2.web_name}\n"
        player2_score += (player2.assists - player1.assists)
    else:
        message += "Assists: equal\n"

    if player1.ict_index_rank > player2.ict_index_rank:
        message += f"ICT Rank: {player1.first_name} {player1.web_name}\n"
        player1_score += 2
    elif player2.ict_index_rank > player1.ict_index_rank:
        message += f"ICT Rank: {player2.first_name} {player2.web_name}\n"
        player2_score += 2
    else:
        message += "ICT Rank: equal\n"

    if player1.dreamteam_count > player2.dreamteam_count:
        message += f"Dream Team Appearances: {player1.first_name} {player1.web_name}\n"
        player1_score += (player1.dreamteam_count - player2.dreamteam_count)
    elif player2.dreamteam_count > player1.dreamteam_count:
        message += f"Dream Team Appearances: {player2.first_name} {player2.web_name}\n"
        player2_score += (player2.dreamteam_count - player1.dreamteam_count)
    else:
        message += "Dream Team Appearances: equal\n"

    if float(diff_dict[player2.team.lower()]) > float(diff_dict[player1.team.lower()]):
        message += f"next matches difficulties: {player1.first_name} {player1.web_name}\n"
        player1_score += 4
    elif float(diff_dict[player1.team.lower()]) > float(diff_dict[player2.team.lower()]):
        message += f"next matches difficulties: {player2.first_name} {player2.web_name}\n"
        player2_score += 4
    else:
        message += "next matches difficulties are equal\n"

    result = player1.web_name if player1_score > player2_score else player2.web_name
    message = f"I recommend \U0001F3C5 {result} \U0001F3C5\n" \
              + f"{player1.first_name} {player1.web_name} \U0001F19A {player2.first_name} {player2.web_name}\n" \
              + message + CHANNEL_AND_BOT_ID
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)


def team(update, context):
    # TODO more user friendly
    try:
        manager_id = int(''.join(context.args))
    except Exception as e:
        message = "Possibly you have entered a wrong input\n" + CHANNEL_AND_BOT_ID
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        return
    req = requests.get(f"https://fantasy.premierleague.com/api/entry/{manager_id}/")
    data = req.json()
    message = f"Manager: {data['player_first_name']} {data['player_last_name']}\n" + \
              f"Team Name: {data['name']} - Overall Rank: {data['summary_overall_rank']}\n" + \
              f"GW {CURRENT_GW} Team:\n"

    if req.status_code != 200:
        message = "Unable to Team with this ID :(\n" + CHANNEL_AND_BOT_ID
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        return
    req = requests.get(f"https://fantasy.premierleague.com/api/entry/{manager_id}/event/{CURRENT_GW}/picks/")

    players = req.json()['picks']
    i = 0
    for item in players:
        message += STATS[STATS.id == item['element']].web_name.item() + ' - ' if item['is_captain'] == False else STATS[
                                                                                                                      STATS.id ==
                                                                                                                      item[
                                                                                                                          'element']].web_name.item() + '(C)' + ' - '
        i += 1
        if i == 11:
            message = message[:-3]
            message += "\n" + SPLITTER + "\n"
    message = message[:-3] + '\n' + CHANNEL_AND_BOT_ID
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    # -------------------- HANDLERS --------------------------------


player_stat_handler = CommandHandler('player', player_stats)
dispatcher.add_handler(player_stat_handler)

popular_players_handler = CommandHandler('popular_players', popular_players)
dispatcher.add_handler(popular_players_handler)

popular_forwards_handler = CommandHandler('popular_forwards', popular_forwards)
dispatcher.add_handler(popular_forwards_handler)

popular_midfielders_handler = CommandHandler('popular_midfielders', popular_midfielders)
dispatcher.add_handler(popular_midfielders_handler)

popular_defenders_handler = CommandHandler('popular_defenders', popular_defenders)
dispatcher.add_handler(popular_defenders_handler)

popular_goalkeepers_handler = CommandHandler('popular_goalkeepers', popular_goalkeepers)
dispatcher.add_handler(popular_goalkeepers_handler)

onfire_players_handler = CommandHandler('onfire_players', onfire_players)
dispatcher.add_handler(onfire_players_handler)

onfire_forwards_handler = CommandHandler('onfire_forwards', onfire_forwards)
dispatcher.add_handler(onfire_forwards_handler)

onfire_midfielders_handler = CommandHandler('onfire_midfielders', onfire_midfielders)
dispatcher.add_handler(onfire_midfielders_handler)

onfire_defenders_handler = CommandHandler('onfire_defenders', onfire_defenders)
dispatcher.add_handler(onfire_defenders_handler)

onfire_goalkeepers_handler = CommandHandler('onfire_goalkeepers', onfire_goalkeepers)
dispatcher.add_handler(onfire_goalkeepers_handler)

next_games_handler = CommandHandler('next_games', next_games)
dispatcher.add_handler(next_games_handler)

easy_matches_handler = CommandHandler('easy_games', easy_matches)
dispatcher.add_handler(easy_matches_handler)

hard_matches_handler = CommandHandler('hard_games', hard_matches)
dispatcher.add_handler(hard_matches_handler)

help_handler = CommandHandler('help', help)
dispatcher.add_handler(help_handler)

coin_flip_handler = CommandHandler('flip_coin', coin_flip)
dispatcher.add_handler(coin_flip_handler)

deadline_handler = CommandHandler('deadline', deadline)
dispatcher.add_handler(deadline_handler)

compare_handler = CommandHandler('compare', compare)
dispatcher.add_handler(compare_handler)

team_handler = CommandHandler('team', team)
dispatcher.add_handler(team_handler)

start_handler = CommandHandler('start', hello)
dispatcher.add_handler(start_handler)

unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(unknown_handler)

#  -------------------- RUN --------------------------------
updater.start_polling()
job_queue.start()
updater.idle()
