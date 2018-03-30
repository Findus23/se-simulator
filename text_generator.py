import os

import jsonlines
import markovify

from markov import MarkovText, MarkovUserName
from utils import *


def get_markov(mode):
    if mode == "Usernames":
        return MarkovUserName
    else:
        return MarkovText


def get_state_size(mode):
    return 1 if mode == "Titles" else 3 if mode == "Usernames" else 2


def load_chain(chainfile, mode):
    markov = get_markov(mode)
    with open(chainfile, 'r') as myfile:
        data = myfile.read()
        print("using existing file\n")
        return markov.from_json(data)


def generate_chain(sourcedir, chainfile, mode):
    combined_cains = None
    chainlist = []
    markov = get_markov(mode)
    i = 0
    with jsonlines.open(sourcedir + "/{type}.jsonl".format(type=mode), mode="r") as content:
        for text in content:
            text = text.strip()
            try:
                chain = markov(text, get_state_size(mode), retain_original=False)
            except KeyError:
                continue
            chainlist.append(chain)
            if i % 100 == 0:
                print(i)
            if i % 1000 == 0:
                subtotal_chain = markovify.combine(chainlist)
                if not combined_cains:
                    combined_cains = subtotal_chain
                else:
                    combined_cains = markovify.combine(models=[combined_cains, subtotal_chain])
                chainlist = []
            i += 1
    subtotal_chain = markovify.combine(chainlist)
    chain = markovify.combine([combined_cains, subtotal_chain])
    with open(chainfile, 'w') as outfile:
        outfile.write(chain.to_json())
    print_ram()
    return chain


def get_chain(url, mode):
    sourcedir = 'raw/{url}'.format(url=url, type=mode)
    chainfile = 'chains/{url}/{type}.chain.json'.format(url=url, type=mode)
    if os.path.exists(chainfile):
        return load_chain(chainfile, mode)
    else:
        return generate_chain(sourcedir, chainfile, mode)


def generate_text(chain: markovify.Text, model):
    if model == "Titles":
        return chain.make_short_sentence(70)
    if model == "Usernames":
        return chain.make_short_sentence(36)
    if model == "Questions" or "Answers":
        paragraphs = []
        sentences = []
        count = int((random.randint(2, 6) * random.randint(3, 6) / 5))
        for _ in range(count):
            sentences.append(chain.make_sentence())
            if random.random() < 0.4:
                paragraphs.append(sentences)
                sentences = []
        paragraphs.append(sentences)
        return "\n".join([" ".join(paragraph) for paragraph in paragraphs])
    return chain.make_sentence()


if __name__ == "__main__":
    basedir, mode = get_settings(2)
    if mode not in ["Questions", "Answers", "Titles", "Usernames"]:
        print("error")
        exit()
    chain = get_chain("sites/astronomy.stackexchange.com", mode)
    for _ in range(10):
        # walk = []
        # for text in chain.gen():
        #     if len(walk) > 100:
        #         break
        #     walk.append(text)
        # result = detokenizer.detokenize(walk, return_str=True)
        # print(result.replace("THISISANEWLINE ", "\n"))
        print(chain.make_sentence())
        print("-----------------------------------")

    print_ram()
