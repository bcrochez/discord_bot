# -*-coding:UTF-8 -*

import ast
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


def get_score():
    try:
        f = open(const.TMP_PATH + '/' + const.QUIZ_SCORE_FILE_PATH, 'r+', encoding='utf-8')
    except Exception as e:
        logger.warning("*** impossible d'ouvrir: %s *** - %s", const.QUIZ_SCORE_FILE_PATH, e)
        return

    quiz_score = ast.literal_eval(f.read())
    f.close()

    return quiz_score


def save_score(user_id):
    download_score_file()

    try:
        f = open(const.TMP_PATH + '/' + const.QUIZ_SCORE_FILE_PATH, 'r+', encoding='utf-8')
    except Exception as e:
        logger.warning("*** impossible d'ouvrir: %s *** - %s", const.QUIZ_SCORE_FILE_PATH, e)
        return

    quiz_score = ast.literal_eval(f.read())
    if user_id not in quiz_score:
        quiz_score[user_id] = 1
    else:
        quiz_score[user_id] += 1

    logger.debug(str(quiz_score))
    f.seek(0, 0)
    f.write(str(quiz_score))
    f.close()

    try:
        s3.upload_file(const.QUIZ_SCORE_FILE_PATH)
    except Exception as e:
        logger.warning('Upload error - %s', e)
        return


def download_score_file():
    try:
        s3.download_file(const.QUIZ_SCORE_FILE_PATH)
    except Exception as e:
        logger.warning('Download error - %s', e)
        return


def get_hint(answer):
    hint = ""
    if len(answer) == 1:
        return "\\*"
    for c in answer:
        if c == " ":
            hint += c
            continue
        if random.randint(0, 1):
            hint += "\\*"
        else:
            hint += c
    return hint


class Quiz:

    def __init__(self, default=10):

        self.__running = False  # Is the quiz active or not
        self.default = default
        self.filepath = []
        self.questions = []

        self.current_questions = []
        self.current_channel = None
        self.current = None
        self.answered = False
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
            await ctx.send(':warning: Le nombre de question doit être supérieur ou égal à 1.')
            return

        if self.__running:
            if ctx.message.channel.id != self.current_channel.id:
                await ctx.send(':warning: Un quiz est déjà en cours sur un autre canal, veuillez attendre la fin de '
                               'celui-ci pour lancer un quiz.')
            else:
                await ctx.send(':warning: Un quiz est déjà en cours, veuillez attendre la fin de celui-ci pour '
                               'lancer un quiz.')
        else:
            self.__running = True
            self.current = None
            # copy all question to current_question
            self.current_questions = self.questions
            self.current_channel = ctx.message.channel
            self.remaining_question = self.default

            await ctx.send('@here\n:loudspeaker: **Début du quiz dans 1 minute.**')
            await ctx.send(str(self.default) + ' question(s) dans le quiz')
            await asyncio.sleep(45)
            await self.askqst()

    # stops quiz and init values
    async def stop(self, channel):
        if self.__running and self.current_channel.id == channel.id:
            await self.current_channel.send(':octagonal_sign: Arrêt du quiz en cours. Pour en relancer un !startquiz')
            self.__running = False
            self.current_channel = None
            self.current = None
            self.default = 10
        else:
            await channel.send(':warning: Aucun quiz en cours. !startquiz pour en lancer un.')

    # asks a question
    async def askqst(self):
        if self.__running:
            if self.current is None and self.remaining_question > 0 and len(self.current_questions) > 0:
                await self.current_channel.send(':loudspeaker: **Prochaine question dans 15 secondes.** (' +
                                   str(self.remaining_question) + ' question(s) restante(s))')
                await asyncio.sleep(15)

                await self.ask_question()
            else:
                await self.current_channel.send(':hourglass: **Toutes les questions ont été jouées !**')
                await self.stop(self.current_channel)

    async def ask_question(self):
        if self.__running and self.current is None and self.remaining_question > 0 and len(self.current_questions) > 0:
            qpos = random.randint(0, len(self.current_questions) - 1)
            local_current = self.current_questions[qpos]
            self.current = local_current
            self.current_questions.remove(local_current)

            await self.current_channel.send(":arrow_right: **Question :** " + self.current.question.strip())
            await asyncio.sleep(45)
            await self.show_hint(local_current)

    async def show_hint(self, local_current):
        if self.__running and self.current is not None and self.current.question == local_current.question:
            # if it remains 15 seconds a hint is given
            await self.current_channel.send(":hourglass_flowing_sand: Il vous reste 15 secondes !")
            await self.current_channel.send(":arrow_right: **Indice :** " + get_hint(self.current.answer.strip()))
            await asyncio.sleep(15)

            await self.show_answer(local_current)

    async def show_answer(self, local_current):
        if self.__running and self.current is not None and self.current.question == local_current.question:
            # if time is up asks next question
            await self.current_channel.send(":x: **La bonne réponse était :** " + self.current.answer.strip())
            self.remaining_question -= 1
            self.current = None
            await self.askqst()

    async def parse_answer(self, message):
        if self.__running and not self.answered and self.current_channel.id == message.channel.id and \
                self.current is not None and self.current.answer.lower().strip() == message.content.lower().strip():
            self.answered = True
            champ = message.author
            await message.channel.send(
                ":white_check_mark: **Bonne réponse de** " + champ.mention + " ! (" + self.current.answer.strip() + ")"
            )

            self.remaining_question -= 1
            self.current = None
            self.answered = False

            save_score(str(champ.id))

            await self.askqst()


class Question:

    def __init__(self, question, answer):
        self.question = question
        self.answer = answer


load_quiz()
quiz = Quiz()

logger.info("---- quiz module loaded ----")
