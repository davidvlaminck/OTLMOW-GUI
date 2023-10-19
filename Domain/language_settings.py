import gettext

# Switchen kan door in languages en of nl_BE in te geven
def returnLanguage():
    en = gettext.translation('messages', localedir='../locale/', languages=['nl_BE'])
    en.install()
    return en.gettext