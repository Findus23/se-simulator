import sys


def get_settings(count):
    if len(sys.argv) != count + 1:
        if count == 1:
            return "workplace"
        elif count == 2:
            return "workplace", "Title"

        print("Please specify {x} parameters".format(x=count))
    if count == 1:
        return sys.argv[1]
    elif count == 2:
        return sys.argv[1], sys.argv[2]
