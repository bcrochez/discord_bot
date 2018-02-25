# -*-coding:UTF-8 -*

import logging
import random

import utils.aws_utils as s3
import utils.utils

logger = utils.utils.get_logger('citations', logging.DEBUG)

TMP_PATH = '/tmp'

random.seed()

logger.info("---- start loading citations ----")

names = ['cinema', 'informatique', 'litt_fr', 'sciences', 'transfo', 'philo', 'proverbes']


def load_citations():
    global citations
    global names
    citations = {}
    error_names = []
    for name in names:
        filename = name + '.txt'
        try:
            s3.download_file(filename)
        except Exception as e:
            logger.warning('Download error - %s', e)
            error_names.append(name)
            continue

        try:
            f = open(TMP_PATH+'/'+filename, encoding='utf-8')
        except Exception as e:
            logger.warning("*** impossible d'ouvrir: %s *** - %s", name, e)
            error_names.append(name)
            continue

        citations_tmp = []
        for citation in f.read().split('%'):
            citations_tmp.append(citation.strip())
        citations[name] = citations_tmp
        logger.info("  -- %s file loaded --", name)
        f.close()
    for name in error_names:
        names.remove(name)


citations = {}
load_citations()
    
logger.info("---- citations module loaded ----")


def load_cita_theme(theme):
    global citations
    global names
    if theme not in names:
        names.append(theme)
    try:
        f = open(TMP_PATH+'/'+theme+'.txt', encoding='utf-8')
    except Exception as e:
        names.remove(theme)
        logger.warning("*** impossible d'ouvrir: %s *** - %s", theme, e)
        return 0
    citations_tmp = []
    for citation in f.read().split('%'):
        citations_tmp.append(citation.strip())
    citations[theme] = citations_tmp
    logger.info("  --  %s file load  --", theme)
    f.close()
    return 1


def get_random_citation():
    total = 0
    for name in names:
        total += len(citations[name])
    i = random.randint(0, total-1)
    for name in names:
        if i < len(citations[name]):
            return citations[name][i]
        i -= len(citations[name])


def get_citation_by_theme(theme):
    try:
        i = random.randint(0, len(citations[theme])-1)
        citation = citations[theme][i]
    except KeyError:
        citation = "Le thème " + theme + " n'existe pas ! (thèmes disponible : " + str(names) + ")"
    return citation
