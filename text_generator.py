import jsonlines
import markovify
import os
from nltk.tokenize.moses import MosesDetokenizer, MosesTokenizer

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


def generate_chain(basedir, mode):
    combined_cains = None
    chainlist = []
    markov = get_markov(mode)
    i = 0
    with jsonlines.open(basedir + "/{type}.jsonl".format(type=mode), mode="r") as content:
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


if __name__ == "__main__":
    basedir, mode = get_settings(2)
    if mode not in ["Questions", "Answers", "Titles", "Usernames"]:
        print("error")
        exit()
    chainfile = basedir + '/{type}.chain.json'.format(type=mode)
    if os.path.exists(chainfile):
        chain = load_chain(chainfile, mode)
    else:
        chain = generate_chain(basedir, mode)

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
