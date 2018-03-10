import resource
from xml.etree import ElementTree

import jsonlines
from html2text import HTML2Text

import utils

BASEDIR = utils.get_settings(1)

h = HTML2Text()
h.ignore_links = True
h.unicode_snob = 1
h.ignore_emphasis = True
h.single_line_break = True
i = 0
iterator = ElementTree.iterparse(BASEDIR + "/Posts.xml")
with jsonlines.open(BASEDIR + '/Questions.jsonl', mode="w") as questions, \
        jsonlines.open(BASEDIR + '/Answers.jsonl', mode="w") as answers, \
        jsonlines.open(BASEDIR + "/Titles.jsonl", "w") as titles:
    for event, element in iterator:
        title = element.get('Title')
        if title:
            titles.write(title)
        body = element.get('Body')
        if body:
            text = h.handle(body)
            if element.get('PostTypeId') == "1":
                questions.write(text)
            else:
                answers.write(text)
        element.clear()
        if i % 100 == 0:
            print(i)
        i += 1
print("{number} total entries".format(number=i))
print("used {mb}MB".format(mb=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024))
