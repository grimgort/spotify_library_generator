import datetime
import operator
import json
import os
import random
import re
import argparse
import logging
import spotipy
import time
import argparse
import spotipy.oauth2 as oauth
from spotipy import util

# To access authorised Spotify data
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth

redirect_uri = "http://localhost:9999"

LOG_FILENAME = "logging_rotatingfile_example.out"
logger = logging.getLogger("spotifyTest")
logger.setLevel(logging.DEBUG)
logging.basicConfig(filename="spotilog.txt", level="INFO")


def has_duplicates(input_list):
    return len(input_list) != len(set(input_list))


class Traks:
    def __init__(
        self,
        id_sp,
        artiste,
        album,
        genres,
        track_name,
        energy,
        acousticness,
        danceability,
        instrumentalness,
        liveness,
        loudness,
        speechiness,
        valence,
        tempo,
    ):
        self.id_sp = id_sp
        self.artiste = artiste
        self.album = album
        self.genres = genres
        self.track_name = track_name
        self.energy = energy
        self.acousticness = acousticness
        self.danceability = danceability
        self.instrumentalness = instrumentalness
        self.liveness = liveness
        self.loudness = loudness
        self.speechiness = speechiness
        self.valence = valence
        self.tempo = tempo


class SpotifyInstance:
    def __init__(self):
        self.add_argument()
        self.scope = "user-follow-read playlist-modify-public playlist-modify-private user-read-private user-library-modify user-library-read"
        self.spo = oauth.SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=redirect_uri,
            scope=self.scope,
            cache_path=".cache-{}".format(self.username),
        )

        util.prompt_for_user_token(
            self.username,
            self.scope,
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=redirect_uri,
        )

        self.sp = spotipy.Spotify(auth=self.get_token())
        # self.playlist_id = "0RQmvqO5SVHbMJzPTY4efG"
        self.initial_time = datetime.datetime.now()
        self.number_track_in_playlist = 0
        self.playlist_number = 0

        self.playlist_id = ""
        self.maximum_song_by_playlist = 500
        self.maximum_playlist_to_create = 10
        self.number_max_request1 = 99
        self.number_max_request2 = 49
        # self.number_max_request2 = 5

        # self.final_database = os.environ[
        #     'APPDATA'] + "/spotipyDatabaseFred/database_final.json"
        # self.genres_database = os.environ[
        #     'APPDATA'] + "/spotipyDatabaseFred/database_genres.json"

        self.final_database = "./spotipyDatabaseFred/database_final.json"
        self.genres_database = "./spotipyDatabaseFred/database_genres.json"
        self.artiste_database = "./spotipyDatabaseFred/database_artistes_followed.json"

        return

    def get_token(self):
        token_info = self.spo.get_cached_token()
        if token_info:
            access_token = token_info["access_token"]
            return access_token
        else:
            print("error token : ", token_info)

    def taille_playlist(self):
        # playlist_list_id_to_delete = []
        offset = 0
        for i in range(0, 50):
            playlists = self.sp.user_playlists(
                self.username, limit=self.number_max_request2, offset=offset
            )
            offset += self.number_max_request2
            number_of_plalist = 0
            for playlist in playlists["items"]:
                number_of_plalist += 1
                # if playlist['id'] in playlist_list_id:
                # print("error playlist_list_id deja unfollower")
                # print(playlist_list_id)
                # print(playlist['id'])
                # break
                # if re.search("AuN°[0-9].*", playlist['name']) or re.search(
                # "feature :.*", playlist['name']):
                print("mark playlist to delete :", playlist["name"])
                self.playlist_list_id_to_delete.append(playlist["id"])
            if number_of_plalist < 49:
                break

    def mark_playlist_to_delete(self):
        self.playlist_list_id_to_delete = []
        offset = 0
        for i in range(0, 50):
            playlists = self.sp.user_playlists(
                self.username, limit=self.number_max_request2, offset=offset
            )
            offset += self.number_max_request2
            number_of_playlist = 0
            for playlist in playlists["items"]:
                number_of_playlist += 1
                if self.args.with_playlist_from_genre:
                    if re.search("Xgenre.*", playlist["name"]) or re.search(
                        "genre.*", playlist["name"]
                    ):
                        print("mark playlist to delete :", playlist["name"])
                        self.playlist_list_id_to_delete.append(playlist["id"])

                if self.args.with_playlist_from_feature:
                    if re.search("AuN°[0-9].*", playlist["name"]) or re.search(
                        "feature.*", playlist["name"]
                    ):
                        print("mark playlist to delete :", playlist["name"])
                        self.playlist_list_id_to_delete.append(playlist["id"])

                if re.search("AuN°[0-9].*", playlist["name"]):
                    print("mark playlist to delete :", playlist["name"])
                    self.playlist_list_id_to_delete.append(playlist["id"])
            if number_of_playlist < 49:
                break

    def delete_marked_playlist(self):
        print(self.playlist_list_id_to_delete)
        for playlist in self.playlist_list_id_to_delete:
            self.sp.user_playlist_unfollow(self.username, playlist)

    def calcul_time_token(self):
        time = datetime.datetime.now() - self.initial_time
        print("time = ", time)
        if time >= datetime.timedelta(0, 0, 0, 0, 15, 0, 0):
            print("token refresh")
            self.refresh_token()
            self.initial_time = datetime.datetime.now()
        return

    def refresh_token(self):
        cached_token = self.spo.get_cached_token()
        print("token expire = ", self.spo.is_token_expired(cached_token))
        refreshed_token = cached_token["refresh_token"]
        new_token = self.spo.refresh_access_token(refreshed_token)
        print("new token : ", new_token["access_token"])  # <--
        # also we need to specifically pass `auth=new_token['access_token']`
        self.sp = spotipy.Spotify(auth=new_token["access_token"])
        return new_token

    def get_artist(self, name):
        results = self.sp.search(q="artist:" + name, type="artist")
        items = results["artists"]["items"]
        if len(items) > 0:
            return items[0]
        else:
            return None

    def get_artist_followed(self):
        artist_list = []
        artist_id = ""

        # for i in range(0, 1):
        for i in range(0, 50):
            if i == 0:
                artist_followed = self.sp.current_user_followed_artists(
                    limit=self.number_max_request2, after=None
                )
            else:
                artist_followed = self.sp.current_user_followed_artists(
                    limit=self.number_max_request2, after=artist_id
                )
            for key in artist_followed["artists"]["items"]:
                artist_list.append([key, key["genres"], key["name"]])
                artist_id = key["id"]
            if artist_followed["artists"]["next"] == None:
                break
        artiste_name_list = []
        for key, genre, name in artist_list:
            artiste_name_list.append(name)
        self.save_tracks_database_to_file(artiste_name_list, self.artiste_database)
        return artist_list

    def complete_database(self, database):
        track_id = []
        self.track_list = []
        album_name_list = []
        track_name = []
        artiste_name_list = []
        genre_name_list = []
        for key in database:
            traks = Traks(
                key[0],
                key[1],
                key[2],
                key[3],
                key[4],
                key[5],
                key[6],
                key[7],
                key[8],
                key[9],
                key[10],
                key[11],
                key[12],
                key[13],
            )
            self.track_list.append(traks)

        database_temporary = self.get_liked_track()
        # logger.info('database liked: %s', database_temporary)
        # with open("./database_liked.json", 'w', encoding='utf-8') as fichier:
        #     json.dump(database_temporary, fichier, ensure_ascii=False, indent=4)
        track_list2 = []
        for key in database_temporary:
            traks2 = Traks(
                key[0],
                key[1],
                key[2],
                key[3],
                key[4],
                key[5],
                key[6],
                key[7],
                key[8],
                key[9],
                key[10],
                key[11],
                key[12],
                key[13],
            )
            track_list2.append(traks2)
        compteur = 0
        for key in track_list2:
            compteur += 1
            add_track = True
            # print(key)
            # for title_liked_exist in key.id_sp:
            # print(genre)
            for key2 in self.track_list:
                if re.search(key.id_sp, key2.id_sp):
                    add_track = False

            if add_track:
                try:
                    database.append(database_temporary[compteur - 1])
                except Exception:
                    database.append(database_temporary[compteur - 1])
                    continue

        artiste_list = self.get_artist_followed()
        # with open("./database_liked.json", 'w', encoding='utf-8') as fichier:
        #     json.dump(artiste_list, fichier, ensure_ascii=False, indent=4)
        artiste_number = 0
        for key, genre, name in artiste_list:
            artiste_number += 1
            print(artiste_number, name)
            album, album_name_liste = self.show_artist_albums(key)
            # les 3 boucles dégueulasse permete de vérifier si on a déja l'album dans la self.track_list pour éviter les doublon
            album_exist = False
            for track in self.track_list:
                for album_name in album:
                    if re.search(album_name["name"], track.album):
                        album_exist = True
            if not album_exist:
                for album_objet in album:
                    print(album_objet["name"], name)
                    self.calcul_time_token()
                    trakts = self.show_album_tracks(album_objet)
                    track_id_of_album, track_name_of_album = self.add_trakts_id_to_list(
                        trakts
                    )
                    track_id.extend(track_id_of_album)
                    track_name.extend(track_name_of_album)
                    for track in track_id_of_album:
                        album_name_list.append(album_objet["name"])
                        artiste_name_list.append(name)
                        genre_name_list.append(genre)
        if len(track_id) != 0:
            (
                energy,
                acousticness,
                danceability,
                instrumentalness,
                liveness,
                loudness,
                speechiness,
                valence,
                tempo,
            ) = self.audio_features_list(track_id)
        if len(track_id) != 0 and len(energy) != 0:
            for i in range(0, len(track_id) - 1):
                try:
                    database.append(
                        [
                            track_id[i],
                            artiste_name_list[i],
                            album_name_list[i],
                            genre_name_list[i],
                            track_name[i],
                            energy[i],
                            acousticness[i],
                            danceability[i],
                            instrumentalness[i],
                            liveness[i],
                            loudness[i],
                            speechiness[i],
                            valence[i],
                            tempo[i],
                        ]
                    )
                except Exception:
                    database.append(
                        [
                            track_id[i],
                            artiste_name_list[i],
                            album_name_list[i],
                            genre_name_list[i],
                            track_name[i],
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                        ]
                    )
                    continue
        # self.save_tracks_database_to_file(database, self.final_database)
        return database

    # def create_database(self):
    #     database = []
    #     track_id = []

    #     database = self.get_liked_track()

    #     artiste_list = self.get_artist_followed()
    #     for key, genre, name in artiste_list:
    #         album, album_name = (self.show_artist_albums(key))
    #         for key in album:
    #             self.calcul_time_token()
    #             trakts = (self.show_album_tracks(key))
    #             track_id, track_name = self.add_trakts_id_to_list(trakts)
    #             print(track_id)
    #             energy, acousticness, danceability, instrumentalness, liveness, loudness, speechiness, valence, tempo = self.audio_features_list(
    #                 track_id)
    #             # print("energy",energy)
    #             if len(track_id) != 0 and len(energy) != 0:
    #                 for i in range(0, len(track_id) - 1):
    #                     # print("i=",i)
    #                     # print(key['name'])
    #                     # print(track_id[i], track_name[i])
    #                     # print(energy[i])
    #                     try:
    #                         database.append([
    #                                         track_id[i], name,  album_name, genre,                                         track_name[i], energy[i], acousticness[i],
    #                                         danceability[i], instrumentalness[i],
    #                                         liveness[i], loudness[i], speechiness[i],
    #                                         valence[i], tempo[i]
    #                                     ])
    #                     except Exception:
    #                         database.append([
    #                             track_id[i], name,  album_name, genre,track_name[i], None, None, None, None, None,
    #                             None, None, None, None, album_name
    #                         ])
    #                         continue
    #     return database

    def show_artist_albums(self, artist):
        albums = []
        albums_name = []
        results = self.sp.artist_albums(
            artist["id"], album_type="album", country="FR", limit=40
        )
        for key in results["items"]:
            if key["album_type"] == "album":
                albums.append(key)

        # cette fonction bug. elle renvoit tout les albums_type. les list sont hyper longue mais les premier résultat sont toujorus les albulms
        # while results['next']:
        #     results = self.sp.next(results)
        #     albums.extend(results['items'])
        # with open("./database_liked.json", 'w', encoding='utf-8') as fichier:
        #        json.dump(albums, fichier, ensure_ascii=False, indent=4)

        logger.info("Total albums: %s", len(albums))
        unique = set()  # skip duplicate albums
        album_output = []
        for album in albums:
            name = album["name"].lower()
            if (name not in unique) and (name != None):
                logger.info("ALBUM: %s", name)
                unique.add(name)
                # self.show_album_tracks(album)
                album_output.append(album)
                albums_name.append(album["name"])
        # self.album_list.extend(album_output)
        return album_output, albums_name

    def audio_features_list(self, trakts_id_liste):
        energy = []
        acousticness = []
        danceability = []
        instrumentalness = []
        liveness = []
        loudness = []
        speechiness = []
        valence = []
        tempo = []
        if self.args.database_without_feature:
            for key in trakts_id_liste:
                energy.append(None)
                acousticness.append(None)
                danceability.append(None)
                instrumentalness.append(None)
                liveness.append(None)
                loudness.append(None)
                speechiness.append(None)
                valence.append(None)
                tempo.append(None)
                return (
                    energy,
                    acousticness,
                    danceability,
                    instrumentalness,
                    liveness,
                    loudness,
                    speechiness,
                    valence,
                    tempo,
                )

        try:
            number_trak_boucle = 0
            list_key = []
            feature_list = []
            # print("trakts_id_liste",trakts_id_liste)
            for key in trakts_id_liste:
                # print("fred1", key)
                number_trak_boucle += 1
                list_key.append(key)
                if len(
                    list_key
                ) == self.number_max_request1 or number_trak_boucle == len(
                    trakts_id_liste
                ):
                    feature_list.extend(self.sp.audio_features(list_key))
                    list_key.clear()
            # print("feature_list", feature_list)

            for key in feature_list:
                # print(key)
                if key != None:
                    energy.append(key["energy"])
                    acousticness.append(key["acousticness"])
                    danceability.append(key["danceability"])
                    instrumentalness.append(key["instrumentalness"])
                    liveness.append(key["liveness"])
                    loudness.append(key["loudness"])
                    speechiness.append(key["speechiness"])
                    valence.append(key["valence"])
                    tempo.append(key["tempo"])
                else:
                    energy.append(None)
                    acousticness.append(None)
                    danceability.append(None)
                    instrumentalness.append(None)
                    liveness.append(None)
                    loudness.append(None)
                    speechiness.append(None)
                    valence.append(None)
                    tempo.append(None)
        except:
            for key in trakts_id_liste:
                energy.append(None)
                acousticness.append(None)
                danceability.append(None)
                instrumentalness.append(None)
                liveness.append(None)
                loudness.append(None)
                speechiness.append(None)
                valence.append(None)
                tempo.append(None)
                continue
        return (
            energy,
            acousticness,
            danceability,
            instrumentalness,
            liveness,
            loudness,
            speechiness,
            valence,
            tempo,
        )

    def playlist_from_genres_pattern(self, genres_name):
        # print("processing playlist : ", genres_name)
        list_track = []
        for key in self.track_list:
            # print(key)
            if isinstance(key.genres, list):  # Check if key.genres is a list
                for genre in key.genres:
                    # print(genre)
                    if re.search(genres_name, genre):
                        # print("fred",genre)
                        list_track.append(key.id_sp)
                        break
            else:
                if re.search(genres_name, key.genres):
                    # print("fred",genre)
                    list_track.append(key.id_sp)

        playlist_name = "genre pat : " + str(genres_name)
        # print(len(list_track),len(list_track))
        # print(playlist_name)
        self.add_list_of_trackts(
            list_track, self.maximum_playlist_to_create, playlist_name
        )

    def playlist_from_genres(self, genres_name):
        # print("processing playlist : ", genres_name)
        list_track = []
        for key in self.track_list:
            if isinstance(key.genres, list):  # Check if key.genres is a list
                for genre in key.genres:
                    if genre == genres_name:
                        list_track.append(key.id_sp)
                        break
            else:
                if key.genres == genres_name:
                    list_track.append(key.id_sp)

        playlist_name = "Xgenre : " + str(genres_name)
        print(playlist_name, len(list_track))
        # print(playlist_name)
        self.add_list_of_trackts(
            list_track, self.maximum_playlist_to_create, playlist_name
        )

    def playlist_from_feature(self, feature_name, min_max, value_arg):
        print("processing playlist : ", feature_name)
        feature_dico = {}
        b = []
        for key in self.track_list:
            feature = {
                "energy": key.energy,
                "acousticness": key.acousticness,
                "danceability": key.danceability,
                "instrumentalness": key.instrumentalness,
                "liveness": key.liveness,
                "loudness": key.loudness,
                "speechiness": key.speechiness,
                "valence": key.valence,
                "tempo": key.tempo,
            }
            if feature[feature_name] != None:
                feature_dico[key.id_sp] = feature[feature_name]
        # print(feature_dico)
        if feature_dico != {}:
            if min_max == True:
                playlist_name = "feature inverse : " + feature_name
                feature_dico = sorted(feature_dico.items(), key=lambda kv: kv[1])
                # print(feature_dico)
                if value_arg != None:
                    for key, value in feature_dico:
                        # print(key,value)
                        if value < value_arg:
                            b.append(key)
                else:
                    b = [x[0] for x in feature_dico]
            else:
                playlist_name = "feature : " + feature_name
                feature_dico = sorted(
                    feature_dico.items(), key=lambda kv: kv[1], reverse=True
                )
                if value_arg != None:
                    for key, value in feature_dico:
                        if value > value_arg:
                            b.append(key)
                else:
                    b = [x[0] for x in feature_dico]
            # b = [x[0] for x in feature_dico]
            # print("len(b)=", len(b))
            # print(playlist_name, len(b))
            self.add_list_of_trackts(b, 1, playlist_name)

    def show_album_tracks(self, album):
        tracks = []
        results = self.sp.album_tracks(album["id"])
        tracks.extend(results["items"])
        while results["next"]:
            results = self.sp.next(results)
            if results["items"] != None:
                tracks.extend(results["items"])
        for i, track in enumerate(tracks):
            logger.info("%s. %s", i + 1, track["name"])
        return tracks

    def add_library_playlist(self):
        if self.args.with_playlist_from_genre:
            self.playlist_from_genres_pattern("french")
            self.playlist_from_genres_pattern("classical")
            list_genres = self.print_genres()
            for key in list_genres:
                self.playlist_from_genres(key)

        if self.args.with_playlist_from_feature:
            self.playlist_from_feature("energy", True, 0.5)
            self.playlist_from_feature("acousticness", True, 0.5)
            self.playlist_from_feature("danceability", True, 0.5)
            self.playlist_from_feature("instrumentalness", True, 0.5)
            self.playlist_from_feature("liveness", True, 0.5)
            self.playlist_from_feature("loudness", True, 0.5)
            self.playlist_from_feature("speechiness", True, None)
            self.playlist_from_feature("valence", True, 0.5)
            self.playlist_from_feature("tempo", True, 100)

            self.playlist_from_feature("energy", False, 0.5)
            self.playlist_from_feature("acousticness", False, 0.5)
            self.playlist_from_feature("danceability", False, 0.5)
            self.playlist_from_feature("instrumentalness", False, 0.5)
            self.playlist_from_feature("liveness", False, 0.5)
            self.playlist_from_feature("loudness", False, 0.5)
            self.playlist_from_feature("speechiness", False, None)
            self.playlist_from_feature("valence", False, 0.5)
            self.playlist_from_feature("tempo", False, 100)
        
        self.big_playlist_from_database()

    def create_or_read_database(self):
        # if self.complete == True:
        #     logger.info("create database")
        #     database = self.create_database()
        #     self.save_tracks_database_to_file(database, self.final_database)
        if self.args.complete2 == True:
            logger.info("create database")
            database = self.read_database(self.final_database)

            database = self.complete_database(database)
            self.save_tracks_database_to_file(database, self.final_database)
        else:
            logger.info("use database processing")
            database = self.read_database(self.final_database)
            # self.add_trakts_id_to_list(self.read_database(self.path_to_save))
            # self.feature_list = self.read_database(self.path_to_save_feature)

        self.track_list = []
        for key in database:
            traks = Traks(
                key[0],
                key[1],
                key[2],
                key[3],
                key[4],
                key[5],
                key[6],
                key[7],
                key[8],
                key[9],
                key[10],
                key[11],
                key[12],
                key[13],
            )
            self.track_list.append(traks)

        if self.args.complete2 == True:
            list_genres = self.print_genres()
            self.save_tracks_database_to_file(list_genres, self.genres_database)
        else:
            list_genres = self.read_database(self.genres_database)

        print(list_genres)

    def big_playlist_from_database(self):
        random.shuffle(self.track_list)
        list_of_id = []
        classical = 0
        # limite le nombre de music classic par playlist (0 ici)
        maximum_of_classical_music = 0
        for key in self.track_list:
            if "classical" in key.genres:
                # print("classical = ",classical)
                classical += 1
                # if classical > (len(self.track_list) / 15):
                if classical > maximum_of_classical_music:
                    continue
            list_of_id.append(key.id_sp)

        self.add_list_of_trackts(list_of_id, self.maximum_playlist_to_create, "AuN°")

    def print_genres(self):
        list_genres = []
        for key in self.track_list:
            if isinstance(key.genres, list):  # Check if key.genres is a list
                for key2 in key.genres:
                    if key2 not in list_genres:
                        list_genres.append(key2)
            else:
                if key.genres not in list_genres:
                    list_genres.append(key.genres)
        return list_genres

    def save_tracks_database_to_file(self, traks, path_to_save):
        if not os.path.exists(os.path.dirname(path_to_save)):
            try:
                os.makedirs(os.path.dirname(path_to_save))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        print(path_to_save)
        with open(path_to_save, "w") as outfile:
            json.dump(traks, outfile, indent=4)

    def read_database(self, file_to_read):
        if not os.path.exists(file_to_read):
            return []
            # raise Exception(
            #     "database don t exist.launch complete process first")
        with open(file_to_read) as json_file:
            traks = json.load(json_file)
        return traks

    def user_playlist_add_tracks_error(self, list_9500_track, playlist_id):
        i = 0
        while i < 500:
            i += 1
            try:
                # print(list_9500_track)
                self.sp.user_playlist_add_tracks(
                    self.username, playlist_id, list_9500_track
                )
                break
            except spotipy.client.SpotifyException as e:
                if e.http_status == 429:
                    print(e.http_status)
                    time.sleep(1)
                    continue
                elif e.http_status == 401:
                    self.refresh_token()
                    continue
                else:
                    print(e)
                    continue
                    # raise e

    def add_list_of_trackts(
        self, trakts_id, number_max_playlist_wanted, playlist_base_name
    ):
        logger.info("add_list_of_trackt")
        self.calcul_time_token()
        random.shuffle(trakts_id)
        list_9500_track = []
        number_track_in_playlist = 0
        track_number_request = 0
        total_trakt = 0
        playlist_number = 1
        date = datetime.datetime.now().strftime("%m/%d/%Y")
        playlist_name = playlist_base_name + str(playlist_number) + " : " + str(date)
        print("add new plalist : ", playlist_name)
        playlist = self.sp.user_playlist_create(self.username, playlist_name)
        playlist_id = playlist["id"]
        # print("traks_id", trakts_id)
        print("traks to add", len(trakts_id))
        for track in trakts_id:
            list_9500_track.append(track)
            track_number_request += 1
            number_track_in_playlist += 1
            total_trakt += 1
            # print("traks to add", len(trakts_id))
            # print("total trakt processed = ", total_trakt)
            if (
                track_number_request == self.number_max_request1
                or len(trakts_id) == total_trakt
            ):
                # logger.info("add traks to plalist : "+ list_9500_track)
                # print("add short list")
                # print("len list added", len(list_9500_track))
                # raise Exception()
                self.user_playlist_add_tracks_error(list_9500_track, playlist_id)
                list_9500_track.clear()
                track_number_request = 0
            if number_track_in_playlist >= self.maximum_song_by_playlist:
                playlist_number += 1
                if playlist_number > number_max_playlist_wanted:
                    break
                playlist_name = (
                    playlist_base_name + str(playlist_number) + " : " + str(date)
                )

                print("add new plalist : ", playlist_name)
                playlist = self.sp.user_playlist_create(self.username, playlist_name)
                playlist_id = playlist["id"]
                number_track_in_playlist = 0

    def add_trakts_id_to_list(self, tracks):
        dico = {}
        dico2 = {}
        for track in tracks:
            dico[track["id"]] = track["name"]
        l = list(dico.items())
        random.shuffle(l)
        dico = dict(l)
        print("len(l) : ", len(l))
        for key, value in dico.items():
            if value not in dico2.values():
                dico2[key] = value
            # else:
            # print("track duplicate deleted : ", value)
        trakts_id_list = []
        trakts_name_list = []

        for key, value in dico2.items():
            trakts_id_list.append(key)
            trakts_name_list.append(value)
        return trakts_id_list, trakts_name_list

    def get_liked_track(self):
        database = []
        track_name = []
        track_id = []
        offset = 0
        for i in range(0, 50):
            # with open("./database_liked.json", 'w', encoding='utf-8') as fichier:
            #     json.dump(database, fichier, ensure_ascii=False, indent=4)
            trak = self.sp.current_user_saved_tracks(
                limit=self.number_max_request2, offset=offset
            )
            offset += self.number_max_request2
            # with open("./database_liked2.json", 'w', encoding='utf-8') as fichier:
            #     json.dump(trak, fichier, ensure_ascii=False, indent=4)
            # print(trak['items'])
            # track_id, trak_name = self.add_trakts_id_to_list(trak['items'])
            # list_track_id.append(track_id)
            for key in trak["items"]:
                # print(key['track']['id'])
                # print(key['track']['name'])
                # for name in key['track']['artists']:
                # artiste_name = name['name']
                # print(name['name'])
                track_id.append(key["track"]["id"])
                track_name.append(key["track"]["name"])
                # list_trak.append((key['track']['id'],key['track']['name'] ))
            if trak["next"] == None:
                break

        (
            energy,
            acousticness,
            danceability,
            instrumentalness,
            liveness,
            loudness,
            speechiness,
            valence,
            tempo,
        ) = self.audio_features_list(track_id)

        if len(track_id) != 0 and len(energy) != 0:
            for i in range(0, len(track_id) - 1):
                # print("i=",i)
                # print(key['name'])
                # print(track_id[i], track_name[i])
                # print(energy[i])
                try:
                    database.append(
                        [
                            track_id[i],
                            "titre liked",
                            "titre liked",
                            "titre liked",
                            track_name[i],
                            energy[i],
                            acousticness[i],
                            danceability[i],
                            instrumentalness[i],
                            liveness[i],
                            loudness[i],
                            speechiness[i],
                            valence[i],
                            tempo[i],
                        ]
                    )
                except Exception:
                    database.append(
                        [
                            track_id[i],
                            "titre liked",
                            "titre liked",
                            "titre liked",
                            track_name[i],
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                        ]
                    )
                    continue

        return database

    def add_argument(self):
        parser = argparse.ArgumentParser(description="give credential for spotify")
        parser.add_argument(
            "--client_id",
            required=True,
            help="give \
                client id. see : https://developer.spotify.com/documentation/general/guides/app-settings/ ",
        )

        parser.add_argument(
            "--client_secret",
            required=True,
            help="give \
                client id. see : https://developer.spotify.com/documentation/general/guides/app-settings/ ",
        )

        parser.add_argument(
            "--username",
            required=True,
            help="give your \
        spotify username ",
        )

        parser.add_argument(
            "--complete",
            action="store_true",
            help="rebuild complete database (don t reuse existing database)",
        )

        parser.add_argument(
            "--with_playlist_from_genre",
            action="store_true",
            help="create a playlist with the French and classic genre",
        )

        parser.add_argument(
            "--with_playlist_from_feature",
            action="store_true",
            help="create a playlist with spotify feature (energy, acousticness, danceability,...)",
        )

        parser.add_argument(
            "--database_without_feature",
            action="store_true",
            help="create a database without spotify feature (energy, acousticness, danceability,...)",
        )

        parser.add_argument(
            "--complete2",
            action="store_true",
            help="create a database without spotify feature (energy, acousticness, danceability,...)",
        )

        self.args = parser.parse_args()
        # print(args.client_id)
        self.client_id = self.args.client_id
        self.client_secret = self.args.client_secret
        self.username = self.args.username
        self.complete = self.args.complete


if __name__ == "__main__":
    print("spotify begin script")
    spotifyInstance = SpotifyInstance()
    spotifyInstance.refresh_token()
    spotifyInstance.mark_playlist_to_delete()

    debut = time.time()
    logger.info("debut create_or_read_database: %s", debut)
    spotifyInstance.create_or_read_database()
    fin = time.time()
    # Calcul du temps écoulé
    temps_ecoule = fin - debut
    logger.info("temp ecoule create_or_read_database: %s", temps_ecoule)

    debut = time.time()
    logger.info("debut add_library_playlist: %s", debut)
    spotifyInstance.add_library_playlist()
    fin = time.time()
    # Calcul du temps écoulé
    temps_ecoule = fin - debut
    logger.info("temp ecoule add_library_playlist: %s", temps_ecoule)

    spotifyInstance.delete_marked_playlist()
    # main()
