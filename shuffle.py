import utils
from models import *
from extra_data import site_colors

query = Question.select().order_by(SQL("RAND()"))

count = query.count()
utils.save_question_count(count)
i = 0
for question in query:
    question.random = i
    i += 1
    if i % 50 == 0:
        print("{}/{}".format(i, count))
    question.save()
