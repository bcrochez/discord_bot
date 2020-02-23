import ast
import logging
import random

import discord

from module import *
import utils.aws_utils as s3
import utils.constants as const
import utils.emoji_utils as emoji_utils
import utils.utils as utils

logger = utils.get_logger('commands', logging.INFO)


def load_admins():
    try:
        s3.download_file(const.ADMINS_ID)
    except Exception as e:
        logger.warning('Download error - %s', e)
        return []
    try:
        f = open(const.TMP_PATH + '/' + const.ADMINS_ID, 'r+', encoding='utf-8')
    except Exception as e:
        logger.warning("*** impossible d'ouvrir: %s *** - %s", const.ADMINS_ID, e)
        return []

    admins_content = ast.literal_eval(f.read())
    f.close()

    return admins_content


admins = load_admins()


# BOT COMMANDS

def get_commands(bot):

    # @bot.command()
    # async def echo(ctx, *, message):
    #    await ctx.send(message)

    @bot.command()
    async def tableflip(ctx):
        """Flips a table"""
        await ctx.send("(╯°□°）╯︵ ┻━┻")

    @bot.command()
    async def add(ctx, left: int, right: int):
        """Adds two numbers together."""
        await ctx.send(left + right)

    @bot.command()
    async def roll(ctx, dice: str):
        """Rolls a dice in NdN format."""
        try:
            rolls, limit = map(int, dice.split('d'))
        except Exception as error:
            logger.warning(error)
            await ctx.send('Format has to be in NdN!')
            return

        result = ', '.join(str(random.randint(1, limit)) for _ in range(rolls))
        await ctx.send(result)

    @bot.command(description='For when you wanna settle the score some other way')
    async def choose(ctx, *choices: str):
        """Chooses between multiple choices."""
        await ctx.send(random.choice(choices))

    @bot.command()
    async def repeat(ctx, times: int, content='repeating...'):
        """Repeats a message multiple times."""
        for i in range(times):
            await ctx.send(content)

    @bot.command()
    async def joined(ctx, member: discord.Member):
        """Says when a member joined."""
        await ctx.send('{0.name} joined in {0.joined_at}'.format(member))

    @bot.group(pass_context=True)
    async def cool(ctx):
        """Says if a user is cool.

        In reality this just checks if a subcommand is being invoked.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send('No, {0.subcommand_passed} is not cool'.format(ctx))

    @cool.command(name='bot')
    async def _bot(ctx):
        """Is the bot cool?"""
        await ctx.send('Yes, the bot is cool.')

    @bot.command()
    async def citation(ctx, *theme):
        """Affiche une citation"""
        if len(theme) > 0:
            random_citation = citations.get_citation_by_theme(theme[0])
        else:
            random_citation = citations.get_random_citation()
        logger.debug('Citation : %s', random_citation)
        await ctx.send(random_citation)

    # @bot.command()
    # async def punir(member: discord.Member):
    #    await  ctx.send('{0.name} est puni(e) !'.format(member))

    @bot.command(pass_context=True)
    async def count(ctx):
        """Compte le nombre d'emoji utilisé"""
        id_server = str(ctx.guild.id)
        emoji_utils.download_emoji_file(logger)

        if ctx.message.mentions:
            id_member = str(ctx.message.mentions[0].id)
            emoji_count = emoji_utils.count_emoji_by_server_and_nick(id_server, id_member, logger)
        else:
            emoji_count = emoji_utils.count_emoji_by_server(id_server, logger)
        visible_emojis = bot.emojis
        visible_emojis_count = []
        for emoji in visible_emojis:
            if str(emoji.id) in emoji_count:
                visible_emojis_count.append([emoji, emoji_count[str(emoji.id)]])

        visible_emojis_count = sorted(visible_emojis_count, key=lambda v: v[1], reverse=True)

        i = 0
        while i < 10 and i < len(visible_emojis_count):
            await ctx.send(str(visible_emojis_count[i][0])+' a été utilisé '+str(visible_emojis_count[i][1])+' fois',)
            i += 1

    # Quiz part here, don't touch if you don't know what you are doing
    @bot.command()
    async def startquiz(ctx, *number):
        """Démarre le quiz"""
        if ctx.message.author.id in admins:
            await quiz.start_quiz(ctx, number)
        else:
            await ctx.send(':warning: Seul un admin peut lancer le quiz.')

    @bot.command()
    async def statsquiz(ctx):
        """Affiche les scores du quiz"""
        quiz.download_score_file()
        quiz_score = quiz.get_score()
        if quiz_score is None:
            return

        guild = ctx.message.guild
        visible_members_score = []
        for member in guild.members:
            if str(member.id) in quiz_score:
                visible_members_score.append([member.nick if member.nick is not None else member.name, quiz_score[str(member.id)]])

        if len(visible_members_score) == 0:
            await ctx.send("Aucun score d'enregistré !")
        else:
            visible_members_score = sorted(visible_members_score, key=lambda v: v[1], reverse=True)

            i = 0
            while i < 10 and i < len(visible_members_score):
                await ctx.send(str(visible_members_score[i][0])+' : '+str(visible_members_score[i][1])+' point(s)',)
                i += 1

    @bot.command()
    async def stopquiz(ctx):
        """Arrête le quiz"""
        if ctx.message.author.id in admins:
            await quiz.stop_quiz(ctx)
        else:
            await ctx.send(':warning: Seul un admin peut lancer le quiz.')
