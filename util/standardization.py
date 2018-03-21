import re
import string
import unicodedata


SLOT_REGEX = re.compile('\(.*\)')  # ("\\(.*\\|.*\\)")
PUNCTUATION = '!"#$%&()*+,/:;<=>?@[\\]^_`{|}~-'
CONCAT = '.'

def standardization(item: str, p_char_to_remove=PUNCTUATION, p_char_to_concat=CONCAT) -> str:
    # lower
    item = item.lower()
    # remove '\n'
    item = item.strip('\n')
    # Remplace les caractères accentués
    item = ''.join((c for c in unicodedata.normalize('NFD', item) if unicodedata.category(c) != 'Mn'))
    # Supprime les caractères spéciaux
    # maketrans crée une table de transfo de "" vers "", en supprimant tous les caractères appartenant à la chaine PONCTUATION
    item = item.translate(item.maketrans(p_char_to_remove, " " * len(p_char_to_remove)))
    item = item.translate(item.maketrans("", "", p_char_to_concat))

    # remove ' '
    item = item.strip()
    # remove(bla bla)
    item = re.sub(SLOT_REGEX, '', item)
    # strip punctuation
    #item = item.translate(string.punctuation)
    #met les nombres en digit
    item = re.sub(u"\d", "dddd", item)
    # supprime les espaces de debut / fin et doubles espaces
    item = " ".join(item.split())

    return item