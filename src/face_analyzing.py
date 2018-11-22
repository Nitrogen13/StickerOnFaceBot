import random
from numpy import average, min, max


def get_random_message(faces):
    phrases = []
    if len(faces) == 1:  # Single person analyzes
        # Age
        phrases.append('I bet your age is between %s and %s' %
                       (str(faces[0].get('AgeRange').get('Low')),
                        str(faces[0].get('AgeRange').get('High'))))
        phrases.append('Your age is between %s and %s, isn\'t it?' %
                       (str(faces[0].get('AgeRange').get('Low')),
                        str(faces[0].get('AgeRange').get('High'))))
        phrases.append('Your seems older than %s, sorry' % str(faces[0].get('AgeRange').get('Low')))
        phrases.append('What I want to say is that you probably younger than %s ^)'
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
        # Emotions
        for emotion in faces[0].get('Emotions'):
            emotion_type = emotion.get('Type')
            confidence = emotion.get('Confidence')
            if (emotion_type == 'HAPPY') & (confidence > 95):
                phrases.append('Smile suits you)')
                phrases.append('Happy people live longer, so you will too')
                phrases.append('You happiness makes me happy too)')
            if (emotion_type == 'SAD') & (confidence > 95):
                phrases.append('Why are you sad?(')
                phrases.append('Don\'t be upset!')
                phrases.append('Sadness is useless feeling, stop it')
            if (emotion_type == 'ANGRY') & (confidence > 95):
                phrases.append('Are you mad at me?')
                phrases.append('Calm down, don\'t be so angry')
                phrases.append('Why are so angry?')
            if (emotion_type == 'CONFUSED') & (confidence > 95):
                phrases.append('What are you thinking about?')
                phrases.append('Thinking a lot is bad :P')
                phrases.append('Is something bothering you?')
            if (emotion_type == 'DISGUSTED') & (confidence > 95):
                phrases.append('Don\'t you like something?')
                phrases.append('What made you disgust?')
                phrases.append('Come on, not everything is so bad, do not be disgusted')
            if (emotion_type == 'SURPRISED') & (confidence > 95):
                phrases.append('Did my functionality surprise you?')
                phrases.append('Do not be so surprised, it\'s only bot)')
                phrases.append('O_O <- you')
            if (emotion_type == 'CALM') & (confidence > 95):
                phrases.append('I want to be as calm as you')
                phrases.append('You look very calm')
                phrases.append('^_^')
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
            # Common female
            phrases.append('How pretty you are ;)')
            phrases.append('Hey, miss, how are you?)')
            phrases.append('Can I have your phone number, miss?)')
            phrases.append('Pretty woman, walkin\' down the street...')
            # Beard
            if faces[0].get('Beard').get('Value'):
                phrases.append('O_O, beard, emmm, OK, it\'s your choice, ma\'am')
            # Mustache
            if faces[0].get('Mustache').get('Value'):
                phrases.append('I\'m not sexist, but mustache... Don\'t do it, plz')
    else:  # Group of people analyzes
        # Common phrases
        phrases.append('I\'m lazy to analyze more than one person right now, meh')
        phrases.append('C\'mon guys, do you want me to analyze all of you? (I will not anyway)')
        phrases.append('Wow, it\'ll take some time to recognize all of you')
        phrases.append('%d people in the photo, hmmm..' % len(faces))
        phrases.append('I\'ll be hard to analyze %d people, but I\'ll try' % len(faces))
        # Age, Sex
        max_ages, min_ages, avg_ages, men, women = [], [], [], 0, 0
        for face in faces:
            max_age = face.get('AgeRange').get('High')
            min_age = face.get('AgeRange').get('Low')
            max_ages.append(max_age)
            min_ages.append(min_age)
            avg_ages.append((max_age + min_age) / 2)
            if face.get('Gender').get('Value') == 'Male':
                men += 1
            else:
                women += 1
        max_age = int(max(max_ages))
        min_age = int(min(min_ages))
        avg_age = int(average(avg_ages))

        if women >= 2:
            phrases.append('Wow, %d beauties in the photo. Like!' % women)
        elif women == 1:
            phrases.append('Only 1 girl in the photo, why?((')
        else:
            phrases.append('No girls, are you serious?')

        if men >= 2:
            phrases.append('What are %d guys doing in this photo?' % men)
        elif men == 1:
            phrases.append('Man, you are so lucky ;)')
        else:
            phrases.append('Girls\' party?')

        if (men == 1) & (women == 1):
            phrases.append('Are you just friends or... beloved???')
        elif (men > 1) & (women > 1):
            phrases.append('I can see %d women and %d men in this photo, am I right?' % (women, men))
            phrases.append('%d women and %d men - party?' % (women, men))
        phrases.append('The oldest of you is %d years old, as I think' % max_age)
        phrases.append('The youngest of you is %d years old, right?' % min_age)
        phrases.append('I counted the average age among you, it is - %d' % avg_age)

    random.shuffle(phrases)
    message = random.choice(phrases)
    return message
