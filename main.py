import os
import random
import logging

import discord
from discord.ext import commands

TOKEN = os.environ.get('TOKEN')

logger = logging.getLogger('discord bot')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)

logger.addHandler(ch)

bot = commands.Bot(command_prefix='!')


def get_user_name(author):
    name = author.name
    nick = "(" + author.nick + ")" if author.nick else ""
    return name + " " + nick


@bot.event
async def on_ready():
    logger.info('Logged in as')
    logger.info(bot.user.name)
    logger.info(bot.user.id)
    logger.info('------')
    servers = bot.servers
    if len(servers) != 0:
        logger.info("Joined servers : ")
        for server in servers:
            logger.info("\t- %s owned by %s", server.name, server.owner.name)
    else:
        logger.info("No server joined")


@bot.event
async def on_message(message):
    name = get_user_name(message.author)
    logger.info("%s - %s - %s : %s", message.timestamp, message.channel.name, name, message.content)
    await bot.process_commands(message)


@bot.command()
async def echo(*, message):
    await bot.say(message)


@bot.command()
async def add(left: int, right: int):
    """Adds two numbers together."""
    await bot.say(left + right)


@bot.command()
async def roll(dice: str):
    """Rolls a dice in NdN format."""
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception as error:
        logger.warning(error)
        await bot.say('Format has to be in NdN!')
        return

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    await bot.say(result)


@bot.command(description='For when you wanna settle the score some other way')
async def choose(*choices: str):
    """Chooses between multiple choices."""
    await bot.say(random.choice(choices))


@bot.command()
async def repeat(times: int, content='repeating...'):
    """Repeats a message multiple times."""
    for i in range(times):
        await bot.say(content)


@bot.command()
async def joined(member: discord.Member):
    """Says when a member joined."""
    await bot.say('{0.name} joined in {0.joined_at}'.format(member))


@bot.group(pass_context=True)
async def cool(ctx):
    """Says if a user is cool.

    In reality this just checks if a subcommand is being invoked.
    """
    if ctx.invoked_subcommand is None:
        await bot.say('No, {0.subcommand_passed} is not cool'.format(ctx))


@cool.command(name='bot')
async def _bot():
    """Is the bot cool?"""
    await bot.say('Yes, the bot is cool.')


if __name__ == '__main__':
    try:
        bot.run(TOKEN)
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
