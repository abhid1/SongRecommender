#
# This class makes song recommendations based off of Spacy's similarity function.
#
import spacy
import pandas as pd
import numpy as np
from scipy import spatial
from sklearn.preprocessing import normalize
from sklearn.metrics.pairwise import cosine_similarity
import json
from operator import itemgetter

nlp = spacy.load("en_core_web_lg")


def create_ui_data(similarities, data):
    ui_dictionary = {}
    index = 0
    for key in similarities:
        ui_list = []
        artist_name = data[index][0][0]
        song_name = data[index][0][1]

        new_key = artist_name + "\t" + song_name

        top_similarities = 0

        for list in similarities[key]:
            ui_list.append(list[3] + "\t" + list[2])
            top_similarities += 1

            if top_similarities == 5:
                break

        ui_dictionary[new_key] = ui_list
        index += 1

    y = json.dumps(ui_dictionary)
    f = open("spacy_ui_data.json", "w")
    f.write(y)


def sort_dictionary(similarities):
    for key in similarities:
        similarities[key] = sorted(similarities[key], key=itemgetter(1), reverse=True)

    return similarities


def run_similarity_analysis(data):
    similarities_dictionary = {}
    for chosen_vector in data:
        for song_vector in data:
            if chosen_vector[0][2] == song_vector[0][2]:
                continue

            computed_song = []
            similarity = cosine_similarity(normalize(chosen_vector[0][3:].reshape(1, -1)),
                                           normalize(song_vector[0][3:].reshape(1, -1)))
            computed_song.append(song_vector[0][2])
            computed_song.append(similarity[0][0])
            computed_song.append(song_vector[0][1])
            computed_song.append(song_vector[0][0])

            if chosen_vector[0][2] not in similarities_dictionary:
                similarities_dictionary[chosen_vector[0][2]] = [computed_song]
            else:
                similarities_dictionary[chosen_vector[0][2]].append(computed_song)

    return similarities_dictionary


def apply_word_embedding(lyrics):
    return nlp(lyrics).vector


def pre_process_data():

    # Delete time signature from data
    songs_df = pd.read_csv('data.csv')
    # songs_df = songs_df.sample(n=25)
    songs_df.drop_duplicates(subset=['id'])
    songs_df = songs_df.reset_index(drop=True)
    del songs_df['time_signature']

    # Replace the newlines
    songs_df['lyrics'] = songs_df['lyrics'].str.replace(r'\n', '')

    data = []

    for ind in songs_df.index:
        song_vector = []
        # song_vector.append(nlp(songs_df['artist'][ind]).vector)
        # song_vector.append(nlp(songs_df['title'][ind]).vector)

        song_vector.append(songs_df['artist'][ind])
        song_vector.append(songs_df['title'][ind])
        song_vector.append(songs_df['id'][ind])
        for val in nlp(songs_df['genre'][ind]).vector:
            song_vector.append(val)

        for val in nlp(songs_df['lyrics'][ind]).vector:
            song_vector.append(val)

        song_vector.append(songs_df['danceability'][ind])
        song_vector.append(songs_df['energy'][ind])
        song_vector.append(songs_df['key'][ind])
        song_vector.append(songs_df['loudness'][ind])
        song_vector.append(songs_df['mode'][ind])
        song_vector.append(songs_df['speechiness'][ind])
        song_vector.append(songs_df['acousticness'][ind])
        song_vector.append(songs_df['instrumentalness'][ind])
        song_vector.append(songs_df['liveness'][ind])
        song_vector.append(songs_df['valence'][ind])
        # song_vector.append(songs_df['tempo'][ind])

        data.append(np.asarray(song_vector).reshape(1, -1))

    return data


data = pre_process_data()
similarities = run_similarity_analysis(data)
similarities = sort_dictionary(similarities)
create_ui_data(similarities, data)

y = json.dumps(similarities)
f = open("spacy_data.json", "w")
f.write(y)