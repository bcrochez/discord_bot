import utils.utils as utils


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
        await bot.process_commands(message)

    @bot.event
    async def on_typing(channel, user, when):
        logger.debug('%s - [TYPING] %s - %s', str(when), utils.get_channel_name(channel), utils.get_user_name(user))
