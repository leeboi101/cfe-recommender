import pickle
import tempfile
from django.contrib.contenttypes.models import ContentType
from django.db.models import F
from ratings.models import Rating
from surprise import accuracy,Dataset, Reader, SVD
from surprise.model_selection import cross_validate
import pickle

def export_ratings_dataset():
    ctype = ContentType.objects.get(app_label='anime', model='anime')
    qs = Rating.objects.filter(active=True,Content_type=ctype)
    qs = qs.annotate(uid=F('user_id'),anime_uid=F('object_id'),score=F('value'))
    return qs.values('userId','animeId','rating') #will be a list of dic vals -> [{}]

def get_data_loader(dataset, columns=['uid', 'anime_uid', 'score']):
    import pandas as pd
    df = pd.DataFrame(dataset)
    df['score'].dropna(inplace=True)
    df['score'] = df['score'].clip(lower=0, upper=10)
    max_rating, min_rating = df.score.max(), df.score.min()
    reader = Reader(rating_scale=(min_rating,max_rating))
    return Dataset.load_from_df(df[columns], reader)


def get_model_acc(trainset, model, use_rmse=True):
         
    testset = trainset.build_testset()
    predictions = model.test(testset)
    if not use_rmse:    
        acc = accuracy.mae(predictions, verbose=True)
    acc = accuracy.rmse(predictions, verbose=True)
    return acc 

def train_surprise_model(n_epochs=20, verbose=True):
    dataset = export_ratings_dataset()
    loaded_data = get_data_loader(dataset)
    model = SVD(n_epochs=n_epochs, verbose=verbose)
    cv_results = cross_validate(algo, loaded_data, measures=['RMSE', "MAE"], cv=4, verbose=True)
    trainset = loaded_data.build_full_trainset()
    model.fit(trainset)
    acc = get_model_acc(trainset, model, use_rmse=True)
    acc_label = int(100 * acc)
    model_name = f"model-{acc_label}" 

def export_model():
    model_algo = None
    with open('model.pk1', 'rb') as f:
        model_data_loaded = pickle.load(f)
        model_algo = model_data_loaded.get('model')
    pass


def load_model():
    pass