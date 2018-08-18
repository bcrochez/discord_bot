import re
import ast

import utils.aws_utils as s3
import utils.utils as utils
import utils.constants as const


# EVENTS

def get_events(bot, logger):

    @bot.event
    async def on_ready():
        logger.info('Logged in as')
        logger.info(bot.user.name)
        logger.info(bot.user.id)
        logger.info('------')
        # listing servers
        servers = bot.servers
        if len(servers) != 0:
            logger.info("Joined servers : ")
            for server in servers:
                logger.info("\t- %s owned by %s", server.name, server.owner.name)
        else:
            logger.info("No server joined")

        logger.info('Bot is ready')

    @bot.event
    async def on_message(message):
        name = utils.get_user_name(message.author)
        channel = utils.get_channel_name(message.channel)
        logger.info("%s - [MESSAGE] %s - %s : %s", message.timestamp, channel, name, message.content)
        if message.author.id != bot.user.id:
            count_emoji(message, logger)
        await bot.process_commands(message)

    @bot.event
    async def on_typing(channel, user, when):
        logger.debug('%s - [TYPING] %s - %s', str(when), utils.get_channel_name(channel), utils.get_user_name(user))


def count_emoji(message, logger):
    if message.server is not None:
        id_server = message.server.id
        id_member = message.author.id
        emoji_list = []

        for word in message.content.split(' '):
            if re.match(const.EMOJI_PATTERN, word):
                id_emoji = re.search(const.EMOJI_PATTERN, word).group(2)
                emoji_list.append(id_emoji)

        if len(emoji_list) > 0:
            logger.debug('%s %s %s', id_server, id_member, emoji_list)

            try:
                s3.download_file(const.STATS_FILE_PATH)
            except Exception as e:
                logger.warning('Download error - %s', e)
                return

            try:
                f = open(const.TMP_PATH + '/' + const.STATS_FILE_PATH, 'r+', encoding='utf-8')
            except Exception as e:
                logger.warning("*** impossible d'ouvrir: %s *** - %s", const.STATS_FILE_PATH, e)
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
                s3.upload_file(const.STATS_FILE_PATH)
            except Exception as e:
                logger.warning('Upload error - %s', e)
                return
