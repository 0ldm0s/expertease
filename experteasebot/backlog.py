BACKLOG_GROUP_CHAT_ID =  # initialize here


def send_to_backlog_group(bot, update):
    text = "User first name: {}\n" \
           "Username (if exists): {}\n" \
           "User chat id: {}\n" \
           "Message: {}\n".format(update.message.from_user.first_name,
                                  update.message.from_user.username,
                                  update.message.from_user.id,
                                  update.message.text)
    bot.send_message(chat_id=BACKLOG_GROUP_CHAT_ID,
                     text=text)
