import json
import boto3

with open('raw_data/full_data.json') as file:
    numbers = json.load(file)
    table = boto3.resource('dynamodb').Table('christmas-texts')
    for n in numbers:
        table.put_item(Item={"phone_number": n['phone_number'],
                        "name": n['name']})