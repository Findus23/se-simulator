import sys

import resource


def print_stats(i, skipped=None):
    print("{number} total entries".format(number=i))
    if skipped:
        print("{number} skipped".format(number=skipped))
    print_ram()


def print_ram():
    print("used {mb}MB".format(mb=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024))


def get_settings(count):
    if len(sys.argv) != count + 1:
        if count == 1:
            return "sites/workplace"
        elif count == 2:
            return "sites/workplace", "Title"

        print("Please specify {x} parameters".format(x=count))
    if count == 1:
        return sys.argv[1]
    elif count == 2:
        return sys.argv[1], sys.argv[2]
