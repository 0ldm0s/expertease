from telegram.ext import (ConversationHandler)
from experteasebot import main, backlog


def current_issues_command(bot, update):
    backlog.send_to_backlog_group(bot, update)
    main.logger.info("Admin {} has asked for current issues."
                     .format(update.message.from_user.first_name))

    if main.ISSUES_QUEUE.qsize() == 0:
        text = "There are no issues waiting for experts."
    else:
        text = "There are currently {} issues waiting for experts."\
            .format(main.ISSUES_QUEUE.qsize())

    text += "\n"
    if not main.EXPERT_ISSUES_DICT:
        text += "No issues are taken care of by experts at the moment.\n"
    else:
        text += "Those are the current issues that are taken care of " \
               "by experts right now:\n"
        for expert, issue in main.EXPERT_ISSUES_DICT.items():
            text += "Issue {} of user {} is taken care of by expert {}.\n"\
                .format(issue['issue_id'], issue['name'], issue['expert_name'])

    bot.send_message(chat_id=update.message.chat_id, text=text)
    return ConversationHandler.END


def send_msg_to_group_command(bot, update, args):
    backlog.send_to_backlog_group(bot, update)
    message = " ".join(args)
    main.logger.info("Admin {} has sent a message to experts' group: {}"
                     .format(update.message.from_user.first_name, message))
    bot.send_message(chat_id=main.EXPERT_GROUP_CHAT_ID, text=message)
    return ConversationHandler.END
