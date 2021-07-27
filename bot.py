from telegram.ext import Updater, CommandHandler
from telegram.ext import MessageHandler, Filters
import logging

#  -------------------- START ------------------------------------
updater = Updater(token='1765909251:AAGX1_LCh8IxCFishKKw3G20Oyl4x5EYqMA', use_context=True)
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


#  -------------------- FUNCTIONS --------------------------------
def hello(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm FPL bot, please talk to me!")


def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


def concat(update, context):
    txt = '-'.join(context.args)
    context.bot.send_message(chat_id=update.effective_chat.id, text=txt)


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


#  -------------------- HANDLERS --------------------------------
concat_handler = CommandHandler('concat', concat)
dispatcher.add_handler(concat_handler)

echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echo_handler)

start_handler = CommandHandler('start', hello)
dispatcher.add_handler(start_handler)

unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(unknown_handler)

#  -------------------- RUN --------------------------------
updater.start_polling()
# updater.idle()