import copy
import datetime

from telegram.ext import Updater, CommandHandler
from telegram.ext import MessageHandler, Filters
import logging
import statistics
import utils
import pandas as pd

#  -------------------- START ------------------------------------
sts = statistics.Statistics()
teams_dict = sts.get_teams()
for key, value in teams_dict.items():
    teams_dict[key] = value.lower()
TEAMS_TO_STRING = ''
SPLITTER = 30 * '~'
STATS = None
LAST_STATS_UPDATE = datetime.datetime.now()
updater = Updater(token='1765909251:AAGX1_LCh8IxCFishKKw3G20Oyl4x5EYqMA', use_context=True)
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
job_queue = updater.job_queue


#  -------------------- FUNCTIONS --------------------------------
def stats_updater(update='', context=''):
    try:
        global STATS
        STATS = pd.DataFrame(sts.update_statistics())
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
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm FPL bot, talk to me!")


def player_stats(update, context):
    # TODO tashaboh esmi ha handle nashude
    player_name = ' '.join(context.args)
    player_name = utils.strip_accents(player_name).lower()
    data = STATS[STATS.web_name == player_name].reset_index()
    if data.shape[0] >= 2:
        response_message = "MORE THAN 1 PLAYER FOUND!\n" + SPLITTER + '\n'
        for index, row in data.iterrows():
            temp = f"first name: {row.first_name}\n" \
                   f"last name : {row.second_name}\n" \
                   f"cost : {row.now_cost / 10}\n" \
                   f"form : {row.form}\n" \
                   f"position : {row.element_type}\n" \
                   f"team : {row.team}\n" \
                   f"total points : {row.total_points}\n" \
                   f"points per game : {row.points_per_game}\n" \
                   f"GW transfer in : {row.transfers_in_event}\n" \
                   f"GW transfer out : {row.transfers_out_event}\n" \
                   f"bonus : {row.bonus}\n" \
                   f"ict_index: {row.ict_index}\n" \
                   f"ict_index_rank : {row.ict_index_rank}\n" \
                   f"minutes : {row.minutes}\n" \
                   f"goals scored : {row.goals_scored}\n" \
                   f"assists : {row.assists}\n" \
                   f"clean sheets : {row.clean_sheets}\n"
            response_message = response_message + temp + SPLITTER + '\n'
        response_message = response_message + "@FPL_TALK \n@persian_fpl_talk_bot"
    else:
        response_message = f"first name: {data.first_name.item()}\n" \
                           f"last name : {data.second_name.item()}\n" \
                           f"cost : {data.now_cost.item() / 10}\n" \
                           f"form : {data.form.item()}\n" \
                           f"position : {data.element_type.item()}\n" \
                           f"team : {data.team.item()}\n" \
                           f"total points : {data.total_points.item()}\n" \
                           f"points per game : {data.points_per_game.item()}\n" \
                           f"GW transfer in : {data.transfers_in_event.item()}\n" \
                           f"GW transfer out : {data.transfers_out_event.item()}\n" \
                           f"bonus : {data.bonus.item()}\n" \
                           f"ict_index: {data.ict_index.item()}\n" \
                           f"ict_index_rank : {data.ict_index_rank.item()}\n" \
                           f"minutes : {data.minutes.item()}\n" \
                           f"goals scored : {data.goals_scored.item()}\n" \
                           f"assists : {data.assists.item()}\n" \
                           f"clean sheets : {data.clean_sheets.item()}\n" \
                           f"goals conceded : {data.goals_conceded.item()}\n" \
                           f"own_goals : {data.own_goals.item()}\n" \
                           f"penalties saved : {data.penalties_saved.item()}\n" \
                           f"penalties missed : {data.penalties_missed.item()}\n" \
                           f"yellow cards : {data.yellow_cards.item()}\n" \
                           f"red cards : {data.red_cards.item()}\n" \
                           f"saves : {data.saves.item()}\n" + SPLITTER + "\n" \
                           f"{sts.get_next_games(data.team.item().lower())}"
    context.bot.send_message(chat_id=update.effective_chat.id, text=response_message)


def popular_players(update, context):
    if len(context.args) == 0:
        count = 10
    else:
        count = int(''.join(context.args))
    df = STATS.sort_values(by=['selected_by_percent'], ascending=False).head(count).reset_index()
    response_message = ""
    for index, row in df.iterrows():
        temp = f"player {index + 1}: {row.web_name}   selected: {row.selected_by_percent}   cost: {int(row.now_cost) / 10}   " \
               f"position: {row.element_type}   team: {row.team}\n"
        response_message = response_message + temp + SPLITTER + '\n'
    response_message = response_message + "@FPL_TALK \n@persian_fpl_talk_bot"
    context.bot.send_message(chat_id=update.effective_chat.id, text=response_message)


def popular_forwards(update, context):
    if len(context.args) == 0:
        count = 10
    else:
        count = int(''.join(context.args))
    df = STATS.sort_values(by=['selected_by_percent'], ascending=False)
    df = df[df.element_type == 'Forward'].head(count).reset_index()
    response_message = ""
    for index, row in df.iterrows():
        temp = f"player {index + 1}: {row.web_name}   selected: {row.selected_by_percent}   cost: {int(row.now_cost) / 10}   " \
               f"team: {row.team}\n"
        response_message = response_message + temp + SPLITTER + '\n'
    response_message = response_message + "@FPL_TALK \n@persian_fpl_talk_bot"
    context.bot.send_message(chat_id=update.effective_chat.id, text=response_message)


def popular_midfielders(update, context):
    if len(context.args) == 0:
        count = 10
    else:
        count = int(''.join(context.args))

    df = STATS.sort_values(by=['selected_by_percent'], ascending=False)
    df = df[df.element_type == 'Midfielder'].head(count).reset_index()
    response_message = ""
    for index, row in df.iterrows():
        temp = f"player {index + 1}: {row.web_name}   selected: {row.selected_by_percent}   cost: {int(row.now_cost) / 10}   " \
               f"team: {row.team}\n"
        response_message = response_message + temp + SPLITTER + '\n'
    response_message = response_message + "@FPL_TALK \n@persian_fpl_talk_bot"
    context.bot.send_message(chat_id=update.effective_chat.id, text=response_message)


def popular_defenders(update, context):
    if len(context.args) == 0:
        count = 10
    else:
        count = int(''.join(context.args))

    df = STATS.sort_values(by=['selected_by_percent'], ascending=False)
    df = df[df.element_type == 'Defender'].head(count).reset_index()
    response_message = ""
    for index, row in df.iterrows():
        temp = f"player {index + 1}: {row.web_name}   selected: {row.selected_by_percent}   cost: {int(row.now_cost) / 10}   " \
               f"team: {row.team}\n"
        response_message = response_message + temp + SPLITTER + '\n'
    response_message = response_message + "@FPL_TALK \n@persian_fpl_talk_bot"
    context.bot.send_message(chat_id=update.effective_chat.id, text=response_message)


def popular_goalkeepers(update, context):
    if len(context.args) == 0:
        count = 10
    else:
        count = int(''.join(context.args))

    df = STATS.sort_values(by=['selected_by_percent'], ascending=False)
    df = df[df.element_type == 'Goalkeeper'].head(count).reset_index()
    response_message = ""
    for index, row in df.iterrows():
        temp = f"player {index + 1}: {row.web_name}   selected: {row.selected_by_percent}   cost: {int(row.now_cost) / 10}   " \
               f"team: {row.team}\n"
        response_message = response_message + temp + SPLITTER + '\n'
    response_message = response_message + "@FPL_TALK \n@persian_fpl_talk_bot"
    context.bot.send_message(chat_id=update.effective_chat.id, text=response_message)


def next_games(update, context):
    if TEAMS_TO_STRING == '':
        teams_to_string()
    team = ' '.join(context.args)
    if team in teams_dict.values():
        response = sts.get_next_games(team)
    else:
        response = 'your input must be one of the following names:\n' + TEAMS_TO_STRING + '@FPL_TALK\n@persian_fpl_talk_bot'
    context.bot.send_message(chat_id=update.effective_chat.id, text=response)


def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


def concat(update, context):
    txt = '-'.join(context.args)
    context.bot.send_message(chat_id=update.effective_chat.id, text=txt)


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


#  -------------------- HANDLERS --------------------------------
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

next_games_handler = CommandHandler('next_games', next_games)
dispatcher.add_handler(next_games_handler)

popular_goalkeepers_handler = CommandHandler('popular_goalkeepers', popular_goalkeepers)
dispatcher.add_handler(popular_goalkeepers_handler)

start_handler = CommandHandler('start', hello)
dispatcher.add_handler(start_handler)

unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(unknown_handler)

#  -------------------- RUN --------------------------------
updater.start_polling()
job_queue.start()
updater.idle()
