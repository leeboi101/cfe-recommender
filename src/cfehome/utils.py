import csv
import datetime
from pprint import pprint
from django.conf import settings


from faker import Faker 

ANIME_CSV = settings.DATA_DIR / "animes.csv"

def validate_date_str(date_text):
    try:
        start_str, end_str = date_text.split(' to ')
        start_date = datetime.datetime.strptime(start_str, '%b %d, %Y')
        end_date = datetime.datetime.strptime(end_str, '%b %d, %Y')
        print(date_text)
        print(start_date.date())
        print(end_date.date())
        return start_date.date(), end_date.date()
    except ValueError:
        # Handle invalid date format
        return None, None
    except AttributeError:
        # Handle case where date_text is None or not a string
        return None, None

def load_anime_data(limit=1):
    with open(ANIME_CSV, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        dataset = []
        for i, row in enumerate(reader):
            _id = row.get("uid")
            try:
                _id = int(_id)
            except:
                _id = None
            start_date,end_date = validate_date_str(row.get('aired'))
            
            data = {
                "uid": _id,
                "title": row.get('title'),
                "synopsis": row.get('synopsis'),
                "start_date": start_date,
                "end_date": end_date,
            }
            dataset.append(data)
            if i + 1 > limit:
                break
        return dataset

def get_fake_profiles(count=10):
    fake = Faker()
    user_data = []
    for _ in range(count):
        profile = fake.profile()
        data = {
            "username": profile.get('username'),
            "email": profile.get('mail'),
            # code for password: "password": make_password(fake.password(length=15)),
            "is_active": True
        }
        if 'name' in profile:
            fname, lname = profile.get('name').split(" ")[:2]
            data['first_name'] = fname
            data['last_name'] = lname
        user_data.append(data)
    return(user_data)