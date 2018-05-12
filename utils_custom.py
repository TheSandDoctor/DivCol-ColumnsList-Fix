import mwclient, mwparserfromhell, pathlib
def allow_bots(text, user):
    user = user.lower().strip()
    text = mwparserfromhell.parse(text)
    for tl in text.filter_templates():
        if tl.name in ('bots', 'nobots'):
            break
    else:
        return True
    for param in tl.params:
        bots = [x.lower().strip() for x in param.value.split(",")]
        if param.name == 'allow':
            if ''.join(bots) == 'none': return False
            for bot in bots:
                if bot in (user, 'all'):
                    return True
        elif param.name == 'deny':
            if ''.join(bots) == 'none': return True
            for bot in bots:
                if bot in (user, 'all'):
                    return False
    return True
def get_em_sizes(template, param):
    #param = str(param)
    #print("Value enter: " + str(template.get(param).value))
    is_not_digit = re.match(r'([0-9]+)em?',str(template.get(param).value))
    if is_not_digit:
        #template.get(param).value = is_not_digit.group(1)
        #if it already has "em", it will catch this regex and return the number bit
        #the raising of a ValueError down below is a catch-all (raises up to save_edit())
        print("Wasn't digit")
        return is_not_digit.group(1)
    try:
        if int(str(template.get(param).value)) < 2:
            print("FALSEEEEEEEE!")
            return False
        elif int(str(template.get(param).value)) == 2:
            #    print("value 2 or less, em 30")
            return 30
        elif int(str(template.get(param).value)) == 3:
            #    print("value 3, em 22")
            return 22
        elif int(str(template.get(param).value)) == 4:
            #        print("value 4, em 18")
            return 18
        elif int(str(template.get(param).value)) == 5:
            #        print("value 5, em 15")
            return 15
        elif int(str(template.get(param).value)) == 6:
            #    print("value 6, em 13")
            return 13
        elif int(str(template.get(param).value)) > 6:
            #    print("value greater 6, em 10")
            return 10
    except ValueError:
        raise
