import unicodedata


def strip_accents(text):
    return ''.join(char for char in
                   unicodedata.normalize('NFKD', text)
                   if unicodedata.category(char) != 'Mn')


if __name__ == '__main__':
    print(strip_accents('Trézéguet'))