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

def validate_genre_str(genre):

    if genre != '[]':
#Strip unwanted characters and convert to list of dictionaries
        genres_list = list(genre.strip("[]"))
        # Extract names of genres

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
   # pprint(genre)
    #pprint('-'100)
    if genre != '[]':
#Strip unwanted characters and convert to list of dictionaries
        genres_list = list(genre.strip("[]"))
        #pprint("genre_list:" + str(genres_list))
        #pprint('-'100)
        # Extract names of genres
        genre_objects = []
        for genre_name in genres_list:
            genre_obj = Genre.objects.filter(name=genre_name).first()
            genre_objects.append(genre_obj)
       # pprint("genre_objects:" + str(genre_objects))
       # pprint('-'*100)
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
    
def create_or_update_anime_with_genres(anime_data):
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

            anime, created = Anime.objects.get_or_create(
                
                id=_id,
                defaults={
                    "title": row.get('title'),
                    "synopsis": row.get('synopsis'),
                    "start_date": start_date,
                    "end_date": end_date,
                    "genre": row.get('genre'),
                    # Exclude 'genre' from defaults since it's a ManyToMany field
                }
            )
            genre_objs = validate_genre(row.get('genres'))
            #genre, _ = Genre.objects.get_or_create(name=row.get('genre'))
            #genre_objs.append(genre)
        
            # Associate genres with the anime
            if genre_objs:
                
                anime.genre.set(genre_objs)
            

            print(f"Processed {'created' if created else 'updated'} Anime: {anime.title} with Genre: {[g.name for g in genre_objs]}")
