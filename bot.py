import datetime

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
TEAMS_TO_STRING = ''
SPLITTER = 30 * '~'
CHANNEL_AND_BOT_ID = '@FPL_TALK\n@persian_fpl_talk_bot'
STATS = None
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


def help(update, context):
    message = """راهنمای استفاده از ربات Persian FPL Talk.
دستور: /player
ورودی: اسم بازیکن به انگلیسی با املا صحیح
خروجی: اطلاعات بازیکن
مثال: 
/player salah
------------------------------------
دستور: /popular_players 
ورودی: تعداد بازیکنان محبوب (اختیاری)
خروجی: اطلاعات بازیکنان محبوب بر اساس درصد مالکیت
مثال:
/popular_players 10
------------------------------------
دستور های /popular_forwards، /popular_midfielders، /popular_defenders و /popular_goalkeepers نیز مانند دستور بالا عمل میکنند برای پست های مختلف.
------------------------------------
دستور: /next_games
ورودی: اسم تیم
خروجی: بازی های بعدی تیم مورد نظر
مثال:
/next_games man utd
------------------------------------
دستور: /easy_games
ورودی: تعداد تیم های مورد نظر (اختیاری)
خروجی: لیست 5 بازی بعدی تیم ها که بر اساس آسانی مرتب شده
مثال:
/easy_games 6
------------------------------------
دستور: /hard_games
ورودی: تعداد تیم های مورد نظر (اختیاری)
خروجی: لیست 5 بازی بعدی تیم ها که بر اساس سختی مرتب شده
مثال:
/hard_games 6
------------------------------------
@FPL_TALK
@FPL_TALK_BOT
"""
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)


def player_stats(update, context):
    # TODO User freindly nist
    player_name = ' '.join(context.args)
    player_name = utils.strip_accents(player_name).lower()
    data = STATS[STATS.web_name == player_name].reset_index()
    if data.shape[0] == 1:
        response_message = "sorry, I cannot find player with this name :( \n" + CHANNEL_AND_BOT_ID
    elif data.shape[0] >= 2:
        response_message = "MORE THAN 1 PLAYER FOUND!\n" + SPLITTER + '\n'
        for index, row in data.iterrows():
            temp = f"first name: {row.first_name}\n" \
                   f"last name : {row.second_name}\n" \
                   f"cost : {row.now_cost / 10}\n" \
                   f"form : {row.form}\n" \
                   f"ict_index_rank : {row.ict_index_rank}\n" + \
                   SPLITTER + "\n" + \
                   f"{row.team.lower()} next games:\n" + SPLITTER + "\n" + sts.get_next_games(row.team.lower())
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
                           + SPLITTER + "\n" + \
                           f"{data.team.item().lower()} next games:\n" + SPLITTER + "\n" + sts.get_next_games(
            data.team.item().lower()) + CHANNEL_AND_BOT_ID

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

popular_goalkeepers_handler = CommandHandler('popular_goalkeepers', popular_goalkeepers)
dispatcher.add_handler(popular_goalkeepers_handler)

next_games_handler = CommandHandler('next_games', next_games)
dispatcher.add_handler(next_games_handler)

easy_matches_handler = CommandHandler('easy_games', easy_matches)
dispatcher.add_handler(easy_matches_handler)

hard_matches_handler = CommandHandler('hard_games', hard_matches)
dispatcher.add_handler(hard_matches_handler)

help_handler = CommandHandler('help', help)
dispatcher.add_handler(help_handler)

start_handler = CommandHandler('start', hello)
dispatcher.add_handler(start_handler)

unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(unknown_handler)

#  -------------------- RUN --------------------------------
updater.start_polling()
job_queue.start()
updater.idle()
