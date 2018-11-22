import random


def get_random_message(faces):
    phrases = []
    if len(faces) == 1:
        # Age
        phrases.append('I bet your age is between %s and %s' %
                       (str(faces[0].get('AgeRange').get('Low')),
                        str(faces[0].get('AgeRange').get('High'))))
        phrases.append('Your age is between %s and %s, isn\'t it?' %
                       (str(faces[0].get('AgeRange').get('Low')),
                        str(faces[0].get('AgeRange').get('High'))))
        phrases.append('Your seems older than %s -_-' % str(faces[0].get('AgeRange').get('Low')))
        phrases.append('What I want to say is that you definitely younger than %s ^)'
                       % str(faces[0].get('AgeRange').get('High')))
        # Eyeglasses
        if faces[0].get('Eyeglasses').get('Value'):
            phrases.append('Cute eyeglasses :)')
            phrases.append('Oh, you have eyeglasses, cool!')
        else:
            phrases.append('If you have no eyeglasses, it means that you have good eyesight)')
        # Sunglasses
        if faces[0].get('Sunglasses').get('Value'):
            phrases.append('Brutal sunglasses')
            phrases.append('Is it sunny today?')
            phrases.append('It\'s sad, that I cannot see your eyes(')
        # Sex dependent features
        if faces[0].get('Gender').get('Value') == 'Male':
            # Beard
            if faces[0].get('Beard').get('Value'):
                phrases.append('Mmmm, nice beard, man!')
                phrases.append('Man, this is not just a beard, it\'s a passport to awesome!')
                phrases.append('Beard makes everything better and... wetter, right?)')
            else:
                phrases.append('Sad, that you have no beard((99(')
                phrases.append('Btw, beard will fit you, fot sure')
            # Mustache
            if faces[0].get('Mustache').get('Value'):
                phrases.append('I like ur mustache, bro!')
                phrases.append('You know? Mustache?')
                phrases.append('Does your mustache brings all the girls to the yard?')
            else:
                phrases.append('No mustache!? :(')
                phrases.append('I think if you had a mustache, the girls would love you))0)')
        else:
            # Beard
            if faces[0].get('Beard').get('Value'):
                phrases.append('O_O, beard, emmm, OK, it\'s your choice, ma\'am')
            # Mustache
            if faces[0].get('Mustache').get('Value'):
                phrases.append('I like ur mustache, bro!')
            else:
                phrases.append('No mustache!? :(')
    else:
        phrases.append('I\'m lazy to analyze more than one person, meh')

    random.shuffle(phrases)
    message = random.choice(phrases)
    return message