from telegram import (ReplyKeyboardRemove)
from telegram.ext import (ConversationHandler)
from experteasebot import main, backlog


def user_sent_feedback(bot, update):
    backlog.send_to_backlog_group(bot, update)
    user = update.message.from_user
    if update.message.chat_id not in main.BLOCKED_USERS_UNTIL_FEEDBACK:
        return ConversationHandler.END

    main.logger.info("User {} has sent feedback: {}."
                     .format(user.first_name, update.message.text))
    issue = main.ISSUES_WAITING_FOR_FEEDBACK[update.message.chat_id]

    text = 'Thank you for sending feedback!\n'

    # When replying, we also need to return the expert's message if exists
    main.dbCur.execute(
        """SELECT message FROM experts WHERE expertchatid = %s;""",
        (str(issue['expert_chat_id']), ))
    fetched = main.dbCur.fetchone()
    if fetched is not None:
        expert_message = fetched['message']
        text += expert_message + "\n\n"

    text += 'If you wish to send another issue, click /start.'
    update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())

    # Now we can enter all data into the database
    main.dbCur.execute("""
        INSERT INTO issues VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
        %s, %s);
        """,
       (issue['issue_id'], issue['name'], issue['chat_id'], issue['expert_name'],
        issue['expert_chat_id'], issue['method'], issue['time_open'],
        issue['time_expert_accepts'], issue['time_solution_submitted'],
        update.message.text, issue['issue'], issue['full_solution'])
    )
    main.dbConn.commit()

    main.BLOCKED_USERS_UNTIL_FEEDBACK.remove(update.message.chat_id)
    del main.ISSUES_WAITING_FOR_FEEDBACK[update.message.chat_id]
    return ConversationHandler.END


def cancel(bot, update):
    backlog.send_to_backlog_group(bot, update)
    user = update.message.from_user
    global ISSUE_DICT
    main.logger.info("User {} canceled submission of issue {}."
                     .format(user.first_name, ISSUE_DICT['issue_id']))
    update.message.reply_text('Bye!',
                              reply_markup=ReplyKeyboardRemove())

    # Deleting the issue.
    ISSUE_DICT = dict()
    main.BLOCKED_USERS_UNTIL_FEEDBACK.remove(update.message.chat_id)

    return ConversationHandler.END
