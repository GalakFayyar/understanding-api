def decode_bio(tokens, prediction):
    curtype = 'O'
    flag_first_loop = True
    result = []
    for token, bio in zip(tokens, prediction):
        if bio.startswith('B-') or bio == 'O':
            if not flag_first_loop:
                result.append([' '.join(current), curtype[2:]])
            curtype = bio
            current = [token]
        elif bio.startswith('I-'):
            if not flag_first_loop and curtype[2:] == bio[2:]:
                current.append(token)
            else:
                if not flag_first_loop:
                    result.append([' '.join(current), curtype[2:]])
                curtype = 'O'
                current = []
        flag_first_loop = False
    if not flag_first_loop:
        result.append([' '.join(current), curtype[2:]])
    return result