import markovify
from nltk.tokenize.moses import MosesDetokenizer, MosesTokenizer

tokenizer = MosesTokenizer()
detokenizer = MosesDetokenizer()


class POSifiedText(markovify.Text):
    def word_split(self, sentence):
        return tokenizer.tokenize(sentence)

    def word_join(self, words):
        return detokenizer.detokenize(words, return_str=True)
