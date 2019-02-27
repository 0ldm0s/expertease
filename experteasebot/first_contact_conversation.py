from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
import telegram
from experteasebot.backlog import send_to_backlog_group
from experteasebot import main
from datetime import datetime as dt


def start(bot, update):
    """Initiated by user"""
    send_to_backlog_group(bot, update)
    if update.message.chat_id in main.BLOCKED_USERS_UNTIL_FEEDBACK:
        main.logger.info("User {} tried to send another issue while a feedback "
                         "for previous issue was not submitted."
                         .format(update.message.from_user.first_name))
        text = "New issues cannot be submitted right now.\n"
        try:
            issue = main.ISSUES_WAITING_FOR_FEEDBACK[update.message.chat_id]
            text += "Please reply 'Yes' if the assistance you " \
                    "received was helpful and 'No' otherwise."
        except KeyError:
            text += "Please wait for an expert to respond to your " \
                    "previous issue."

        update.message.reply_text(text)
        return ConversationHandler.END

    # global ISSUE_ID
    main.ISSUE_ID += 1

    user = update.message.from_user
    main.ISSUE_DICT = {'name': user.first_name, 'chat_id':
                       update.message.chat_id,
                       'issue_id': main.ISSUE_ID}
    main.BLOCKED_USERS_UNTIL_FEEDBACK.append(main.ISSUE_DICT['chat_id'])

    main.logger.info("A new user has connected. First name: {}, last name: {}, "
                     "username: {}. Assigned issue ID: {}"
                     .format(user.first_name, user.last_name,
                             user.username, main.ISSUE_ID))
    reply_keyboard = [['Video', 'Text']]

    update.message.reply_text(
        'Hi! We are Expert-Ease, and we will find you an expert that can '
        'help you with whatever it is you need on Wordpress.\n'
        'Do you want to send us a description of the issue using '
        'video or text?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                         one_time_keyboard=True))

    return main.METHOD


def method(bot, update):
    """Supposed to get 'video' or 'text' methods from user"""
    send_to_backlog_group(bot, update)
    user = update.message.from_user
    main.logger.info("Method chosen by {}: {}"
                .format(user.first_name, update.message.text))
    text = 'Great! Please send us a '

    if update.message.text == 'Video':
        text += 'link to a video (possibly with sound) describing the issue.' \
                ' Please shoot the video using the extension Loom, which will ' \
                'best demonstrate the issue.'
        main.ISSUE_DICT['method'] = 'video'
    elif update.message.text == 'Text':
        text += 'detailed walkthrough of the issue.'
        main.ISSUE_DICT['method'] = 'text'

    update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
    return main.DESCRIPTION


def description(bot, update):
    """Gets brief description of the issue"""
    send_to_backlog_group(bot, update)
    user = update.message.from_user
    main.ISSUE_DICT['issue'] = update.message.text
    main.ISSUE_DICT['time_open'] = dt.now().strftime("%d.%m.%y %H:%M:%S")
    main.ISSUES_QUEUE.put(main.ISSUE_DICT)

    main.logger.info("Issue of {} submitted. "
                     "Given issue: {}".format(user.first_name,
                                              update.message.text))
    update.message.reply_text('An expert user will help you shortly. Thanks for'
                              ' your patience!\nReference number for the '
                              'issue: {}'.format(main.ISSUE_DICT['issue_id']))

    # Sends the issue to the experts' group
    bot.send_message(chat_id=main.EXPERT_GROUP_CHAT_ID,
                     text=("{} has requested help! If you're available to "
                           "assist, please reply /accept\n"
                           "*Note:* if you accept an issue (that has not been "
                           "taken already), ExpertEaseBot will "
                           "send you a private message with further details."
                           .format(user.first_name)),
                     parse_mode=telegram.ParseMode.MARKDOWN)
    main.logger.info("The issue of user {} has been sent to experts group."
                .format(user.first_name))
    return ConversationHandler.END
