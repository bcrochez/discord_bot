import utils.utils as utils
import utils.emoji_utils as emoji_utils
import module.quiz as quiz


# EVENTS

def get_events(bot, logger):

    @bot.event
    async def on_ready():
        logger.info('Logged in as')
        logger.info(bot.user.name)
        logger.info(bot.user.id)
        logger.info('------')
        # listing servers
        guilds = bot.guilds
        if len(guilds) != 0:
            logger.info("Joined servers : ")
            for guild in guilds:
                logger.info("\t- %s owned by %s", guild.name, guild.owner.name)
        else:
            logger.info("No server joined")

        logger.info('Bot is ready')

    @bot.event
    async def on_message(message):
        name = utils.get_user_name(message.author)
        channel = utils.get_channel_name(message.channel)
        logger.info("%s - [MESSAGE] %s - %s : %s", message.created_at, channel, name, message.content)
        if message.author.id != bot.user.id:
            emoji_utils.count_emoji(message, logger)
            await quiz.parse_answer(message)
        await bot.process_commands(message)

    @bot.event
    async def on_typing(channel, user, when):
        logger.debug('%s - [TYPING] %s - %s', str(when), utils.get_channel_name(channel), utils.get_user_name(user))
