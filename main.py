from dictionary import Interface
from dictionary import Dictionary
from dictionary import CREATE_BOW
from dictionary import SAVE_REPRESENTATIVES
from dictionary import SAVE_REVIEW
from dictionary import CLOSE
import sys


def create_bow(interface):
    dic = interface.read_dictionary()
    if not dic:
        return

    while not dic.sources:
        interface.read_configuration(dic)
        if not interface.save_configuration(dic):
            dic.sources = None

    interface.export_new_bow(dic)


def save_representatives(interface):
    dic = interface.read_dictionary(new=False)
    if not dic:
        return

    interface.import_bow(dic)


def save_review(interface):
    dic = interface.read_dictionary(new=False)
    if not dic:
        return

    interface.import_review(dic)


def main():
    # Only for develop
    file = open('foo.err', 'w')
    sys.stdout = file
    sys.stderr = file

    Dictionary.PrepareStatements()
    interface = Interface()

    mode = None
    while (mode != CLOSE):
        mode = interface.choose_mode()
        if mode == CREATE_BOW:
            create_bow(interface)

        if mode == SAVE_REPRESENTATIVES:
            save_representatives(interface)

        if mode == SAVE_REVIEW:
            save_review(interface)

    return


if __name__ == "__main__":
    main()
