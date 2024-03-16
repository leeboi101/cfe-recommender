import csv
import datetime
import ast
from pprint import pprint
from django.conf import settings
from anime.models import Anime, Genre

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

def validate_genre_str(genres):
    pprint(genres)
    pprint('-'*100)
    if genres != '[]':
#Strip unwanted characters and convert to list of dictionaries
        genres_list = ast.literal_eval(genres)
        # Extract names of genres
        pprint(genres_list)
        pprint('-'*100)
        # Check if all genre names were found
        all_exist = ''
        for name in genres_list:
            # Check if genre already exists
            existing_genre = Genre.objects.filter(name=name).first()
            if existing_genre is None:
                return name
            else: 
                all_exist = name
        return all_exist
    return None

def validate_genre(genre):
    if genre and genre != '[]':
        # Strip unwanted characters and convert to list of dictionaries
        genres_list = ast.literal_eval(genre)
        genre_objects = []
        for genre_name in genres_list:
            genre_obj = Genre.objects.filter(name=genre_name).first()
            genre_objects.append(genre_obj)
        return genre_objects
    return None


def load_genre_data(limit=1):
    with open(ANIME_CSV, newline='', encoding='utf-8') as csvfile:
        reader  = csv.DictReader(csvfile)
        dataset = []
        for i, row in enumerate(reader):
            if i + 1 > limit:
                break
            genre = validate_genre_str(row.get('genre'))
            data = {
                'name': genre,
            }
            dataset.append(data)
            if i + 1 > limit:
                break
        return dataset
    
def create_or_update_anime_with_genres(limit=1):
    with open(ANIME_CSV, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        dataset = []
        for i, row in enumerate(reader):
            if i + 1 > limit:
                break
            _id = row.get("uid")
            try:
                _id = int(_id)
            except:
                _id = None

            # Fetch existing anime object or create a new one if it doesn't exist
            anime = Anime.objects.get_or_create(id=_id)

            # Validate and fetch genre objects
            genre_objs = validate_genre(row.get('genres'))

            # If genre objects exist, update the many-to-many field
            if genre_objs:
                anime.genre.set(genre_objs)
                anime.save()

            if i + 1 > limit:
                break
    return limit