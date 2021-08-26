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
دستور: /flip_coin
ورودی: نام دو بازیکن که با (-) از هم جدا شده اند
خروجی: اسم یکی از بازیکنان ورودی
مثال:
/flip_coin salah - fernandes
------------------------------------
دستور: /deadline
ورودی: ندارد
خروجی: تاریخ دلاین به میلادی و شمسی
مثال:
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
        playerA.strip()
        playerB.strip()
    except Exception as e:
        message = "Invalid input:(\ntwo players must be divided by (-)\nFor example salah - fernandes\n" \
                  + CHANNEL_AND_BOT_ID
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        return

    player1 = STATS.loc[STATS.web_name.str.contains(playerA)]
    player2 = STATS.loc[STATS.web_name.str.contains(playerB)]
    player1_score = 0
    player2_score = 0
    diff_dict = dict(sts.calculate_difficulties())
    message = ""
    if float(player1.form.item()) > float(player2.form.item()):
        message += f"Form: {player1.web_name}\n"
        player1_score += 5
    elif float(player2.form.item()) > float(player1.form.item()):
        message += f"Form: {player2.web_name}\n"
        player2_score += 5
    else:
        message += "Form: equal\n"

    if player1.goals_scored.item() > player2.goals_scored.item():
        message += f"Goals: {player1.web_name}\n"
        player1_score += (player1.goals_scored.item() - player2.goals_scored.item())
    elif player2.goals_scored.item() > player1.goals_scored.item():
        message += f"Goals: {player2.web_name}\n"
        player2_score += (player2.goals_scored.item() - player1.goals_scored.item())
    else:
        message += "Goals: equal\n"

    if player1.assists.item() > player2.assists.item():
        message += f"Assists: {player1.web_name}\n"
        player1_score += (player1.assists.item() - player2.assists.item())
    elif player2.assists.item() > player1.assists.item():
        message += f"Assists: {player2.web_name}\n"
        player2_score += (player2.assists.item() - player1.assists.item())
    else:
        message += "Assists: equal\n"

    if player1.ict_index_rank.item() > player2.ict_index_rank.item():
        message += f"ICT Rank: {player1.web_name}\n"
        player1_score += 2
    elif player2.ict_index_rank.item() > player1.ict_index_rank.item():
        message += f"ICT Rank: {player2.web_name}\n"
        player2_score += 2
    else:
        message += "ICT Rank: equal\n"

    if player1.dreamteam_count.item() > player2.dreamteam_count.item():
        message += f"Dream Team Appearances: {player1.web_name}\n"
        player1_score += (player1.dreamteam_count.item() - player2.dreamteam_count.item())
    elif player2.dreamteam_count.item() > player1.dreamteam_count.item():
        message += f"Dream Team Appearances: {player2.web_name}\n"
        player2_score += (player2.dreamteam_count.item() - player1.dreamteam_count.item())
    else:
        message += "Dream Team Appearances: equal\n"

    if float(diff_dict[player2.team.item().lower()]) > float(diff_dict[player1.team.item().lower()]):
        message += f"next matches difficulties: {player1.web_name}\n"
        player1_score += 4
    elif float(diff_dict[player1.team.item().lower()]) > float(diff_dict[player2.team.item().lower()]):
        message += f"next matches difficulties: {player2.web_name}\n"
        player2_score += 4
    else:
        message += "next matches difficulties are equal\n"

    result = player1.web_name if player1_score > player2_score else player2.web_name
    message = f"I recommend \U0001F3C5{result}\U0001F3C5\n" \
              + f"{player1.web_name} score: {player1_score} \U0001F19A {player1.web_name} score: {player1_score}\n" \
              + message + CHANNEL_AND_BOT_ID
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)


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

coin_flip_handler = CommandHandler('flip_coin', coin_flip)
dispatcher.add_handler(coin_flip_handler)

deadline_handler = CommandHandler('deadline', deadline)
dispatcher.add_handler(deadline_handler)

compare_handler = CommandHandler('compare', compare)
dispatcher.add_handler(compare_handler)

start_handler = CommandHandler('start', hello)
dispatcher.add_handler(start_handler)

unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(unknown_handler)

#  -------------------- RUN --------------------------------
updater.start_polling()
job_queue.start()
updater.idle()
