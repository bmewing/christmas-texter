import os
import boto3
import random
from datetime import date


def get_name(phone):
    table = boto3.resource('dynamodb').Table('christmas-texts')
    query = table.get_item(Key={'phone_number': phone})
    try:
        output = query['Item']['name']
    except KeyError:
        output = 'Unknown'
    return output


def determine_family(name):
    o = 'ERROR'
    if name in ['Jacob', 'Angie']:
        o = 'Jacob/Angie'
    elif name in ['Joe', 'Claire']:
        o = 'Joe/Claire'
    elif name in ['Mark', 'Amy']:
        o = 'Mark/Amy'
    elif name in ['Sam', 'Mom']:
        o = 'Sam'
    return o


def determine_who(name, to=True):
    family = determine_family(name)
    assignment_to = {
        "Jacob/Angie": ["Mark/Amy",   "Sam",        "Joe/Claire"],
        "Mark/Amy":    ["Joe/Claire", "Jacob/Angie","Sam"],
        "Joe/Claire":  ["Sam",        "Mark/Amy",   "Jacob/Angie"],
        "Sam":         ["Jacob/Angie","Joe/Claire", "Mark/Amy"],
        "ERROR":       ["ERROR",      "ERROR",      "ERROR"]
    }
    assignment_from = {
        "Mark/Amy":    ["Jacob/Angie", "Joe/Claire",  "Sam"],
        "Jacob/Angie": ["Sam",         "Mark/Amy",    "Joe/Claire"],
        "Joe/Claire":  ["Mark/Amy",    "Sam",         "Jacob/Angie"],
        "Sam":         ["Joe/Claire",  "Jacob/Angie", "Mark/Amy"],
        "ERROR":       ["ERROR",       "ERROR",       "ERROR"]
    }
    date_object = date.today()
    year = date_object.strftime("%Y")
    position = (int(year) - 2015) % 3
    if to:
        assignment = assignment_to
    else:
        assignment = assignment_from
    return assignment[family][position]


def update_identity(event, context):
    phone_number = event['userId']
    name = event['currentIntent']['slots']['person_calling']
    code = event['currentIntent']['slots']['secret_code']
    if code != os.environ['secret_code']:
        resp = {
            "dialogAction": {
                "type": "Close",
                "fulfillmentState": "Failed",
                "message": {
                    "contentType": "PlainText",
                    "content": "Your identity cannot be confirmed, goodbye."
                }
            }
        }
    else:
        table = boto3.resource('dynamodb').Table('christmas-texts')
        table.put_item(Item={"phone_number": phone_number,
                        "name": name})
        resp = {
                "dialogAction": {
                    "type": "ElicitIntent",
                    "message": {
                        "contentType": "PlainText",
                        "content": "Great, I've updated your info {}, now, what can I do for you?".format(name)
                    }
                }
            }
    return resp


def verify_identity(event):
    who_to = get_name(event['userId'])
    if who_to == 'Unknown':
        resp = {
            "dialogAction": {
                "type": "ElicitIntent",
                "message": {
                    "contentType": "PlainText",
                    "content": "I'm sorry, but I don't recognize this number. Who is this?"
                }
            }
        }
    else:
        resp = {
            "dialogAction": {
                "type": "Close",
                "fulfillmentState": "Fulfilled",
                "message": {
                    "contentType": "PlainText",
                    "content": ""
                }
            }
        }
    return resp


def getting(event, context):
    print(event)
    stinger = [
        '{t}, it looks like {f} is on deck for getting presents for your family.',
        'I\'m sure {f} will ensure your family has a very merry Christmas!',
        'Do you hear sleigh bells ringing? It must be {f} bringing the Christmas magic!',
        '*bleep bloop* This autonomous robot has calculated that {f} will be providing gifts for {t}\'s family *bloop bleep*'
    ]
    who_to = get_name(event['userId'])
    who_from = determine_who(who_to, to=False)
    print('Message Received From: '+who_to+'\nGETTING FROM: '+who_from)
    resp = verify_identity(event)
    if who_to != "Unknown":
        resp['dialogAction']['message']['content'] = random.choice(stinger).format(f = who_from, t = who_to)
    print(resp)
    return resp


def giving(event, context):
    print(event)
    stinger = [
        'I\'m sure you\'ll make {t}\'s family\'s Christmas merry and bright this year!',
        '{f}, you\'re on point for buying gifts for {t} this year.',
        'When did you gain weight, grow a beard and start ho-ho-hoing all about, {f}? No bother, I\'m sure {t} will be thrilled to get your gifts!'
    ]
    who_from = get_name(event['userId'])
    who_to = determine_who(who_from, to=True)
    print('Message Received From: '+who_from+'\nGIVING TO: '+who_to)
    resp = verify_identity(event)
    if who_from != "Unknown":
        resp['dialogAction']['message']['content'] = random.choice(stinger).format(f = who_from, t = who_to)
    print(resp)
    return resp