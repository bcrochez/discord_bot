# -*-coding:UTF-8 -*

import asyncio
import random
import logging

import utils.utils as utils
import utils.constants as const
import utils.aws_utils as s3

logger = utils.get_logger('quiz', logging.INFO)

logger.info("---- start loading quiz ----")


def load_quiz():
    try:
        s3.download_file(const.QUIZ_PATH)
    except Exception as e:
        logger.warning('Download error - %s', e)
        return


async def start_quiz(ctx, number):
    await quiz.start(ctx, number)


async def stop_quiz(ctx):
    await quiz.stop(ctx.message.channel)


async def parse_answer(message):
    await quiz.parse_answer(message)


class Quiz:

    def __init__(self, default=10):

        self.__running = False  # Is the quiz active or not
        self.default = default
        self.filepath = []
        self.questions = []

        self.current_questions = []
        self.current_channel = None
        self.current = None
        self.remaining_question = 0

        self.loadquestions()

    def loadquestions(self):

        with open(const.TMP_PATH + '/' + const.QUIZ_PATH, 'r+', encoding='utf-8') as self.filepath:
            lines = self.filepath.readlines()

        position = 0

        while position < len(lines):
            data = lines[position].split('\\')
            if len(data) != 2:
                position += 1
            else:
                question = data[0].strip()
                answer = data[1].strip()
                if question is not None and answer is not None:
                    q = Question(question=question, answer=answer)
                    self.questions.append(q)
                position += 1

    # starts quiz
    async def start(self, ctx, number):
        if len(number) > 0 and int(number[0]) > 0:
            self.default = int(number[0])
        elif len(number) > 0:
            await ctx.send('Le nombre de question doit être supérieur ou égal à 1.')
            return

        if self.__running:
            if ctx.message.channel.id != self.current_channel:
                await ctx.send('Un quiz est déjà en cours sur un autre canal, veuillez attendre la fin de celui-ci '
                               'pour lancer un quiz.')
            else:
                await ctx.send('Un quiz est déjà en cours, veuillez attendre la fin de celui-ci pour lancer un quiz.')
        else:
            self.__running = True
            self.current = None
            # copy all question to current_question
            self.current_questions = self.questions
            self.current_channel = ctx.message.channel.id
            self.remaining_question = self.default

            await ctx.send('@here\n:loudspeaker:\n**Début du quiz dans 1 minute.**')
            await ctx.send(str(self.default) + ' question(s) dans le quiz')
            await asyncio.sleep(45)
            await self.askqst(ctx.message.channel)

    # stops quiz and init values
    async def stop(self, channel):
        if self.__running and self.current_channel == channel.id:
            await channel.send('Arrêt du quiz en cours. Pour en relancer un !startquiz')
            self.__running = False
            self.current_channel = None
            self.current = None
            self.default = 10
        else:
            await channel.send('Aucun quiz en cours. !startquiz pour en lancer un.')

    # asks a question
    async def askqst(self, channel):
        if self.__running:
            if self.remaining_question > 0 and len(self.current_questions) > 0:
                await channel.send(':loudspeaker:\n**Prochaine question dans 15 secondes.** (' +
                                   str(self.remaining_question) + ' question(s) restante(s))')
                await asyncio.sleep(15)

                qpos = random.randint(0, len(self.current_questions) - 1)
                local_current = self.current_questions[qpos]
                self.current = local_current
                self.current_questions.remove(local_current)

                await channel.send("Question : " + self.current.question.strip())
                await asyncio.sleep(45)
                if self.current is not None and self.current.question == local_current.question:
                    await channel.send("Il vous reste 15 secondes !")
                    await asyncio.sleep(15)
                    if self.current is not None and self.current.question == local_current.question:
                        await channel.send("La bonne réponse était : " + self.current.answer.strip())
                        self.remaining_question -= 1
                        self.current = None
                        await self.askqst(channel)
            else:
                await channel.send('Toutes les questions ont été jouées !')
                await self.stop(channel)

    async def parse_answer(self, message):
        if self.__running and self.current_channel == message.channel.id:
            if self.current is not None and self.current.answer.lower().strip() == message.content.lower().strip():
                self.remaining_question -= 1
                self.current = None

                await message.channel.send("Bonne réponse !")
                await self.askqst(message.channel)


class Question:

    def __init__(self, question, answer):
        self.question = question
        self.answer = answer


load_quiz()
quiz = Quiz()

logger.info("---- quiz module loaded ----")