#
# This file is responsible for processing and producing an updated csv file. We read the
# Kaggle Data (linked in our proposal) and make requests to the Spotify API.
#

import csv
import requests
import re


def prepare_data(input_file):
    """
    This method will create an unfiltered data matrix consisting of the unique artists and their songs
    from the billboard data.
    :return: unfiltered data matrix
    """

    data = []
    artist_and_songs_dictionary = dict()

    for row in input_file:
        data_dictionary = dict()
        data_dictionary["artist"] = row["Artists"]
        data_dictionary["title"] = row["Name"]
        data_dictionary["genre"] = row["Genre"]
        data_dictionary["lyrics"] = row["Lyrics"]

        if data_dictionary["artist"] in artist_and_songs_dictionary and \
                data_dictionary["title"] not in artist_and_songs_dictionary[data_dictionary["artist"]]:
                    artist_and_songs_dictionary[data_dictionary["artist"]].append(data_dictionary["title"])
                    data.append(data_dictionary)
        elif data_dictionary["artist"] in artist_and_songs_dictionary and \
                data_dictionary["title"] in artist_and_songs_dictionary[data_dictionary["artist"]]:
                    continue
        else:
            data.append(data_dictionary)
            artist_and_songs_dictionary[data_dictionary["artist"]] = [data_dictionary["title"]]

    return data


def get_access_token(client_id, client_secret):
    """
    This method, when given a client_id and client_secret via the spotify developer dashboard,
    will return the access token needed to make requests for song ids and features
    :param client_id: Developer's client id
    :param client_secret: Developer's secret id
    :return: access token
    """

    AUTH_URL = 'https://accounts.spotify.com/api/token'

    # POST
    auth_response = requests.post(AUTH_URL, {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    })

    # convert the response to JSON
    auth_response_data = auth_response.json()

    # save the access token
    access_token = auth_response_data['access_token']

    return access_token


def get_song_id(access_token, song_name, artist):
    """
    This method, when given the access token, song name, and artist name, will return the song id of the
    respective parameters
    :param access_token: user's access token
    :param song_name: song title
    :param artist: artist name
    :return: Spotify id of the song
    """

    headers = {
        'Authorization': 'Bearer {token}'.format(token=access_token)
    }

    artist = artist.split(',')[0]
    song_name = re.sub("'", "", song_name)

    # base URL of all Spotify API endpoints
    BASE_URL = 'https://api.spotify.com/v1/search?q=track:"' + song_name + '"%20artist:"' + artist +\
               '"&type=track'

    # actual GET request with proper header
    r = requests.get(BASE_URL, headers=headers)
    r = r.json()

    spotify_id = ""

    try:
        spotify_id = r["tracks"]['items'][0]["id"]
    except:
        print("artist", artist, "song", song_name)

    return spotify_id


def get_features_for_track(track_id, row):
    """
    This method will get the features given a track id
    :param track_id: Spotify unique id for a track
    :return: Features from spotify for the track
    """

    headers = {
        'Authorization': 'Bearer {token}'.format(token=access_token)
    }

    # base URL of all Spotify API endpoints
    BASE_URL = 'https://api.spotify.com/v1/audio-features/' + track_id

    # actual GET request with proper header
    r = requests.get(BASE_URL, headers=headers)
    r = r.json()

    row["danceability"] = r["danceability"]
    row["energy"] = r["energy"]
    row["key"] = r["key"]
    row["loudness"] = r["loudness"]
    row["mode"] = r["mode"]
    row["speechiness"] = r["speechiness"]
    row["acousticness"] = r["acousticness"]
    row["instrumentalness"] = r["instrumentalness"]
    row["liveness"] = r["liveness"]
    row["valence"] = r["valence"]
    row["tempo"] = r["tempo"]
    row["duration_ms"] = r["duration_ms"]
    row["time_signature"] = r["time_signature"]
    row["id"] = r["id"]

    return r


access_token = get_access_token("6dc8ee95f75043c8b9f7869848ca8a95", "3036419608854dbb996e9388123b9b88")
unfilitered_data = prepare_data(input_file)

ids = []
final_data = []

# Create the final data that consists of lyrics and Spotify features
for row in unfilitered_data:
    song_id = get_song_id(access_token, row["title"], row["artist"])
    if song_id == "":
        continue
    row["id"] = song_id
    try:
        get_features_for_track(song_id, row)
    except:
        continue

    final_data.append(row)

# Construct the new csv file
with open('data.csv', 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, final_data[0].keys())
    dict_writer.writeheader()
    dict_writer.writerows(final_data)

