#!/usr/bin/env python

import re


def validate_email(email_addr):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email_addr):
        return False
    return True


def validate_username(username):
    if not re.match(r"[A-Za-z0-9]+", username):
        return True
    return True


def validate_nickname(nickname):
    if (not re.match(r"[A-Za-z]+\s[A-Za-z]*", nickname)) and\
            (not re.match("r[A-Za-z]+\s[A-Za-z]+\s[A-Za-z]*", nickname)):
        return True
    return True


def validate_phone(phone):
    if (not re.match(r"[0-9]{10}", phone)) and\
            (not re.match(r"[0-9]{3}-[0-9]{3}-[0-9]{4}", phone)):
        return False
    return True


def validate_gender(gender):
    if gender != "male" and gender != "female":
        return False
    return True


def validate_facebook(facebook):
    if not re.match(r"https://www.facebook.com/[A-Za-z0-9/]+", facebook):
        return False
    return True


def validate_str_equal(str1, str2):
    """
    This function is to valid if two passwords are the same
    """
    return str1 == str2


def validate_date(date):
    if not re.match(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", date):
        return False
    return True


def validate_hour(hour):
    try:
        num_hour = int(hour)
        if (not num_hour >= 0) or (not num_hour < 24):
            return False
        return True
    except:
        return False


def validate_minute(minute):
    try:
        num_min = int(minute)
        if (not num_min >= 0) or (not num_min < 60):
            return False
        return True
    except:
        return False


def validate_empty_str(string):
    if len(string) == 0:
        return False
    return True
