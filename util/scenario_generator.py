"""Generate a set of scenarios based on character sequences known to cause problems"""

import csv

from pprint import pprint as pp


# Things that, in themselves, cause problems for operating systems by their presence
TROUBLESOME_CHARACTERS= [
    '#', '%', '?',  # Things that REALLY mess with URL encoding
    '[', ']', '{', '}', '(', ')', '<', '>',  # Parentheses and brackets
    '|', '~', '`', '!', '@', ' ', '$', '^', '&', '*', '+', '=', ',', ';', ':',  # Iffy
    '.', '-', '_',  # Might not need to be encoded at all
    "'", '"',  # Quote marks
    '/', '\\',  # Slashes
    '\t', '\n', '\r\n'  # Control characters
]

FRIN_CHARS_YALL = [
    # TODO: Unicode, umlauts, etc
    # Sort of foreign
    # Generic unicode
    # Esoteric unicode from the twilight zone
]


def write_for_sequence(out_fn: str, charset: list, *, position: int=1):
    """
    :param out_fn: Where to write the list of scenarios
    :param charset: A list of chars to use
    :param position: 0 for start of string, 1 for middle, -1 for end
    :return: 
    """
    with open(out_fn, 'a') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        for c in charset:
            if position == 0:
                sample_str = "{}filename.txt".format(c)
            elif position == -1:
                sample_str = "filename.txt{}".format(c)
            else:
                sample_str = "file{}name.txt".format(c)

            writer.writerow([
                "a sequence containing {} at position {}".format(c, position),
                sample_str
            ])


def verify_readable(filename):
    """Verify this is a readable CSV file (some of the characters we throw in are pretty weird!)"""
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        # Force reading all rows
        pp(list(reader))



if __name__ == '__main__':
    write_for_sequence('../scenarios/special-char-tests.csv', TROUBLESOME_CHARACTERS, position=0)
    write_for_sequence('../scenarios/special-char-tests.csv', TROUBLESOME_CHARACTERS, position=1)
    write_for_sequence('../scenarios/special-char-tests.csv', TROUBLESOME_CHARACTERS, position=2)

    write_for_sequence('../scenarios/encodings-tests.csv', FRIN_CHARS_YALL, position=1)


print('Done writing test cases!')

# print('Verifying ../scenarios/special-char-tests.csv')
# verify_readable('../scenarios/special-char-tests.csv')
#
# print('Verifying ../scenarios/encodings-tests.csv')
# verify_readable('../scenarios/encodings-tests.csv')
