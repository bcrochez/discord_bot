import os
import errno
import ast

import logging
import utils.constants as const


def make_dir(dir_name):
    try:
        os.makedirs(dir_name)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


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


def count_emoji_by_server(id_server, logger):
    emoji_stats = get_emoji_stat(logger)
    if emoji_stats is None:
        return

    emoji_count = {}
    if id_server in emoji_stats:
        for id_member in emoji_stats[id_server]:
            for id_emoji in emoji_stats[id_server][id_member]:
                if id_emoji in emoji_count:
                    emoji_count[id_emoji] += emoji_stats[id_server][id_member][id_emoji]
                else:
                    emoji_count[id_emoji] = emoji_stats[id_server][id_member][id_emoji]

    logger.debug(emoji_count)
    return emoji_count


def count_emoji_by_server_and_nick(id_server, id_member, logger):
    emoji_stats = get_emoji_stat(logger)
    if emoji_stats is None:
        return

    emoji_count = {}
    if id_server in emoji_stats:
        if id_member in emoji_stats[id_server]:
            for id_emoji in emoji_stats[id_server][id_member]:
                if id_emoji in emoji_count:
                    emoji_count[id_emoji] += emoji_stats[id_server][id_member][id_emoji]
                else:
                    emoji_count[id_emoji] = emoji_stats[id_server][id_member][id_emoji]

    logger.debug(emoji_count)
    return emoji_count


def get_emoji_stat(logger):
    try:
        f = open(const.TMP_PATH + '/' + const.STATS_FILE_PATH, 'r+', encoding='utf-8')
    except Exception as e:
        logger.warning("*** impossible d'ouvrir: %s *** - %s", const.STATS_FILE_PATH, e)
        return None

    emoji_stats = ast.literal_eval(f.read())
    f.close()

    return emoji_stats
