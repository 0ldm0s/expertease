from telegram import (ReplyKeyboardMarkup)
from telegram.ext import (ConversationHandler)
import telegram
from datetime import datetime as dt
import time
from experteasebot import main, backlog


def expert_accepts(bot, update):
    backlog.send_to_backlog_group(bot, update)
    expert = update.message.from_user
    if main.ISSUES_QUEUE.empty():  # No users to assist
        bot.send_message(chat_id=main.EXPERT_GROUP_CHAT_ID,
                         text="There is no user that needs assistance"
                              " at the moment, but thank you!")
        main.logger.info("Expert {} wished to assist, but queue is empty."
                         .format(expert.first_name))
        return ConversationHandler.END

    # Updating expert's current issue
    current_issue = main.ISSUES_QUEUE.get()
    current_issue['expert_name'] = expert.first_name
    current_issue['expert_chat_id'] = expert.id
    current_issue['time_expert_accepts'] = dt.now().strftime("%d.%m.%y %H:%M:%S")
    main.EXPERT_ISSUES_DICT[expert.id] = current_issue

    global ISSUE_DICT
    ISSUE_DICT = dict()

    # Notifying the expert that he's taking an issue
    bot.send_message(chat_id=expert.id,
                     text=("Thank you {}! You will help {} on issue {}.\n"
                           "After making the Loom video, please share the "
                           "link here. Thanks!\n"
                           "The issue, as submitted: {}"
                           .format(expert.first_name,
                                   current_issue['name'],
                                   current_issue['issue_id'],
                                   current_issue['issue'])))
    main.logger.info("Expert {} has received issue {}."
                     .format(expert.first_name, current_issue['issue_id']))

    # Updating the user that an expert is connected to him
    bot.send_message(chat_id=current_issue['chat_id'],
                     text="Hey {}! Our expert {} is making a personalized video "
                          "response just for you, as we speak!"
                     .format(current_issue['name'], expert.first_name))
    main.logger.info("User {} has been updated that {} has taken the issue."
                     .format(current_issue['name'], expert.first_name))
    return ConversationHandler.END


def link_from_expert(bot, update):
    backlog.send_to_backlog_group(bot, update)
    if not main.check_if_has_open_issue(update):
        return ConversationHandler.END

    # Check if this is a Loom video:
    if "useloom.com" not in update.message.text.lower():
        update.message.reply_text("This is indeed a link, but not to a Loom "
                                  "video. Please send one!")
        return ConversationHandler.END

    issue = main.EXPERT_ISSUES_DICT[update.message.chat_id]
    issue['time_solution_submitted'] = dt.now().strftime("%d.%m.%y %H:%M:%S")
    issue['full_solution'] = update.message.text
    expert = update.message.from_user
    bot.send_message(chat_id=issue['chat_id'],
                     text="Our expert {} is finished, and sent you the "
                          "following link on issue {}:\n"
                          "{}".format(expert.first_name, issue['issue_id'],
                                      issue['full_solution']))

    # Thanks to expert
    update.message.reply_text("Thank you for helping {} out!"
                              .format(issue['name']))

    main.logger.info("User {} has received link from expert {}. Link: {}"
                     .format(issue['name'],
                             expert.first_name, update.message.text))
    del main.EXPERT_ISSUES_DICT[update.message.chat_id]

    # Feedback phase
    main.ISSUES_WAITING_FOR_FEEDBACK[issue['chat_id']] = issue
    time.sleep(30)
    reply_keyboard = [['Yes', 'No']]
    bot.send_message(chat_id=issue['chat_id'],
                     text="Was the help from {} helpful?"
                          .format(expert.first_name),
                     reply_markup=ReplyKeyboardMarkup(
                         reply_keyboard, one_time_keyboard=True))
    return ConversationHandler.END


def non_link_from_expert(bot, update):
    backlog.send_to_backlog_group(bot, update)
    if not main.check_if_has_open_issue(update):
        return ConversationHandler.END
    update.message.reply_text("This is not a valid link to a video. Try "
                              "sending in the following format:\n"
                              "https://www.useloom.com/share/example")
    return ConversationHandler.END


def collect_message_from_expert_command(bot, update, args):
    backlog.send_to_backlog_group(bot, update)
    message = " ".join(args)
    main.logger.info("Expert {} has requested to use the following message: {}"
                     .format(update.message.from_user.first_name, message))
    main.dbCur.execute("""DELETE FROM experts WHERE expertchatid = %s;""",
                       (str(update.message.chat_id), ))
    main.dbCur.execute("""INSERT INTO experts VALUES (%s, %s, %s);""",
                       (update.message.from_user.first_name,
                        update.message.chat_id,
                        message))
    main.dbConn.commit()
    update.message.reply_text("Thank you {}! The message will be saved in "
                              "our database and sent to users you help in "
                              "the future.\n"
                              "*Note*: at the moment, we allow messages with "
                              "up to 100 characters."
                              .format(update.message.from_user.first_name),
                              parse_mode=telegram.ParseMode.MARKDOWN)
    return ConversationHandler.END
