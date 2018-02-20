import logging


# creating logger
def get_logger(logger_name, level):
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)

    logger.addHandler(ch)

    return logger


# utils function

def get_user_name(author):
    name = author.name
    nick = " (" + author.nick + ")" if hasattr(author, 'nick') and author.nick else ""
    return name + nick


def get_channel_name(channel):
    channel_name = channel.name if channel.name else 'Private channel'
    server = ' (' + channel.server.name + ')' if hasattr(channel, 'server') and channel.server else ''
    return channel_name + server
