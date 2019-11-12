import re
import ast

import utils.aws_utils as s3
import utils.constants as const


def download_emoji_file(logger):
    try:
        s3.download_file(const.EMOJI_COUNT_FILE_PATH)
    except Exception as e:
        logger.warning('Download error - %s', e)
        return


def count_emoji(message, logger):
    """Saves emoji count to server"""
    if message.guild is not None:
        id_server = str(message.guild.id)
        id_member = str(message.author.id)
        emoji_list = []

        for word in message.content.split(' '):
            if re.match(const.EMOJI_PATTERN, word):
                id_emoji = re.search(const.EMOJI_PATTERN, word).group(2)
                emoji_list.append(id_emoji)

        if len(emoji_list) > 0:
            logger.debug('%s %s %s', id_server, id_member, emoji_list)

            download_emoji_file(logger)

            try:
                f = open(const.TMP_PATH + '/' + const.EMOJI_COUNT_FILE_PATH, 'r+', encoding='utf-8')
            except Exception as e:
                logger.warning("*** impossible d'ouvrir: %s *** - %s", const.EMOJI_COUNT_FILE_PATH, e)
                return

            emoji_stats = ast.literal_eval(f.read())
            for id_emoji in emoji_list:
                if id_server not in emoji_stats:
                    emoji_stats[id_server] = {}
                if id_member not in emoji_stats[id_server]:
                    emoji_stats[id_server][id_member] = {}

                if id_emoji not in emoji_stats[id_server][id_member]:
                    emoji_stats[id_server][id_member][id_emoji] = 1
                else:
                    emoji_stats[id_server][id_member][id_emoji] += 1

            logger.debug(str(emoji_stats))
            f.seek(0, 0)
            f.write(str(emoji_stats))
            f.close()

            try:
                s3.upload_file(const.EMOJI_COUNT_FILE_PATH)
            except Exception as e:
                logger.warning('Upload error - %s', e)
                return


# count emoji by server id
def count_emoji_by_server(id_server, logger):
    # open stat file
    emoji_stats = get_emoji_stat(logger)
    # if file is empty
    if emoji_stats is None:
        return

    emoji_count = {}
    if id_server in emoji_stats:
        for id_member in emoji_stats[id_server]:
            # for each emoji in emoji list from one server and one member
            for id_emoji in emoji_stats[id_server][id_member]:
                if id_emoji in emoji_count:
                    emoji_count[id_emoji] += emoji_stats[id_server][id_member][id_emoji]
                else:
                    emoji_count[id_emoji] = emoji_stats[id_server][id_member][id_emoji]

    logger.debug(emoji_count)
    return emoji_count


def count_emoji_by_server_and_nick(id_server, id_member, logger):
    # open stat file
    emoji_stats = get_emoji_stat(logger)
    # if file is empty
    if emoji_stats is None:
        return

    emoji_count = {}
    if id_server in emoji_stats:
        if id_member in emoji_stats[id_server]:
            # for each emoji in emoji list from one server and one member
            for id_emoji in emoji_stats[id_server][id_member]:
                if id_emoji in emoji_count:
                    emoji_count[id_emoji] += emoji_stats[id_server][id_member][id_emoji]
                else:
                    emoji_count[id_emoji] = emoji_stats[id_server][id_member][id_emoji]

    logger.debug(emoji_count)
    return emoji_count


def get_emoji_stat(logger):
    try:
        f = open(const.TMP_PATH + '/' + const.EMOJI_COUNT_FILE_PATH, 'r+', encoding='utf-8')
    except Exception as e:
        logger.warning("*** impossible d'ouvrir: %s *** - %s", const.EMOJI_COUNT_FILE_PATH, e)
        return None

    emoji_stats = ast.literal_eval(f.read())
    f.close()

    return emoji_stats
