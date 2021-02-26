import os
import logging

import discord
from discord.ext import commands

import utils.utils
import commands as cmd
import events


DISCORD_BOT_TOKEN = os.environ.get('TOKEN')

# creating logger
logger = utils.utils.get_logger('discord bot', logging.INFO)

# creating bot
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)
cmd.get_commands(bot)
events.get_events(bot, logger)


# Main function

if __name__ == '__main__':
    try:
        logger.info('Preparing to run bot...')
        bot.run(DISCORD_BOT_TOKEN)
    except Exception as e:
        import sys

        logger.error(sys.exc_info()[0])
        logger.error("---- -----")
        import traceback

        logger.error(traceback.format_exc())
        logger.error("---- -----")
        logger.error(e)
        logger.error("---- ----")
        logger.error("Press Enter to continue ...")
        input()
    finally:
        bot.close()
