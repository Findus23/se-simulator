import resource

import jsonlines
import markovify
from nltk.tokenize.moses import MosesDetokenizer, MosesTokenizer

import utils

detokenizer = MosesDetokenizer()

BASEDIR, mode = utils.get_settings(2)
if mode not in ["Questions", "Answers", "Titles"]:
    mode ="Titles"
chainfile = BASEDIR + '/{type}.chain.json'.format(type=mode)

try:
    with open(chainfile, 'r') as myfile:
        data = myfile.read()
        chain = markovify.Chain.from_json(data)
        # raise FileNotFoundError
        print("using existing file\n")

except FileNotFoundError:
    tokenizer = MosesTokenizer()

    combined_cains = None
    chainlist = []
    i = 0
    with jsonlines.open(BASEDIR + "/{type}.jsonl".format(type=mode), mode="r") as content:
        for text in content:
            tokens = tokenizer.tokenize(text=text.rstrip('\n'))
            chain = markovify.Chain([tokens], (1 if mode == "Titles" else 2))
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

for _ in range(10):
    walk = []
    for text in chain.gen():
        if len(walk) > 100:
            break
        walk.append(text)
    result = detokenizer.detokenize(walk, return_str=True)
    print(result)
    print("-----------------------------------")

print("used {mb}MB".format(mb=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024))
