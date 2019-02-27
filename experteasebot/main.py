from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
import queue
import logging
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import urllib
from experteasebot.commands import admin, expert, user
from experteasebot.first_contact_conversation import start, method, description

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)

# For initial conversation handler with user
METHOD, DESCRIPTION = range(2)
EXPERT_GROUP_CHAT_ID =  # initialize here

# Creating the PostgreSQL database
# Comment the next lines to use local
urllib.parse.uses_netloc.append("postgres")
url = urllib.parse.urlparse(os.environ["DATABASE_URL"])
dbConn = psycopg2.connect(database=url.path[1:], user=url.username,
                          password=url.password, host=url.hostname,
                          port=url.port)
dbCur = dbConn.cursor(cursor_factory=RealDictCursor)

# Global variables
ISSUE_DICT = dict()
ISSUES_QUEUE = queue.Queue()
EXPERT_ISSUES_DICT = dict()
ISSUE_ID = 0
ADMINS = []
BLOCKED_USERS_UNTIL_FEEDBACK = list()
ISSUES_WAITING_FOR_FEEDBACK = dict()


def check_if_has_open_issue(update):
    """Check if this 'expert' (not necessarily an expert) has an open issue"""
    try:
        issue = EXPERT_ISSUES_DICT[update.message.chat_id]
        return True
    except KeyError:
        return False


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "{}" caused error "{}"'.format(update, error))


def main():
    token = "TOKEN"

    # Create the EventHandler and pass it your bot's token.
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states METHOD and DESCRIPTION
    user_conv_handler = ConversationHandler(
        entry_points=[CommandHandler(command='start', callback=start)],
        states={
            METHOD: [RegexHandler(pattern='^(Video|Text)$', callback=method)],
            DESCRIPTION: [MessageHandler(filters=Filters.text,
                                         callback=description)]
        },
        fallbacks=[CommandHandler(command='cancel', callback=user.cancel)],
    )

    expert_accepts_msg_handler = CommandHandler(
        command='accept',
        filters=Filters.chat(EXPERT_GROUP_CHAT_ID),
        callback=expert.expert_accepts
    )

    collect_message_from_expert_command_handler = CommandHandler(
        command="msg",
        callback=expert.collect_message_from_expert_command,
        pass_args=True
    )

    current_issues_msg_handler = CommandHandler(
        command='current_issues',
        filters=Filters.chat(ADMINS),
        callback=admin.current_issues_command
    )

    send_msg_to_group_command_handler = CommandHandler(
        command='send_msg_to_group',
        filters=Filters.chat(ADMINS),
        callback=admin.send_msg_to_group_command,
        pass_args=True
    )

    user_sent_feedback_msg_handler = RegexHandler(
        pattern='^(Yes|No)$',
        callback=user.user_sent_feedback
    )

    expert_sends_link_msg_handler = MessageHandler(
        filters=(Filters.text & Filters.private & Filters.entity('url')),
        callback=expert.link_from_expert
    )

    expert_sends_non_link_msg_handler = MessageHandler(
        filters=(Filters.all & Filters.private),
        callback=expert.non_link_from_expert
    )

    dp.add_handler(user_sent_feedback_msg_handler)
    dp.add_handler(user_conv_handler)
    dp.add_handler(expert_accepts_msg_handler)
    dp.add_handler(collect_message_from_expert_command_handler)
    dp.add_handler(current_issues_msg_handler)
    dp.add_handler(send_msg_to_group_command_handler)
    dp.add_handler(expert_sends_link_msg_handler)
    dp.add_handler(expert_sends_non_link_msg_handler)

    # log all errors
    dp.add_error_handler(error)

    # Retrieving port from environment variable
    port = int(os.environ.get('PORT', '8443'))

    # Start the Bot
    # Usage: webhook for Heroku XOR start_polling for local
    updater.start_webhook(listen="0.0.0.0",
                          port=port,
                          url_path=token)
    updater.bot.set_webhook("https://expertease.herokuapp.com/" + token)
    # updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
