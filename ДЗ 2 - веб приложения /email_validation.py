import re

def fun(s):
    return bool(re.fullmatch(r'[A-Za-z0-9_-]+@[A-Za-z0-9]+\.[A-Za-z]{1,3}', s))

def filter_mail(emails):
    return list(filter(fun, emails))
