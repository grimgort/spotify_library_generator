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
redirect_uri = 'http://localhost:9999'

LOG_FILENAME = 'logging_rotatingfile_example.out'
logger = logging.getLogger('spotifyTest')
logger.setLevel(logging.DEBUG)
logging.basicConfig(filename='spotilog.txt', level='INFO')


class SpotifyInstance:
    def __init__(self):
        self.add_argument()
        self.scope = 'user-follow-read playlist-modify-public playlist-modify-private'
        self.spo = oauth.SpotifyOAuth(client_id=self.client_id,
                                      client_secret=self.client_secret,
                                      redirect_uri=redirect_uri,
                                      scope=self.scope,
                                      cache_path=".cache-{}".format(
                                          self.username))

        util.prompt_for_user_token(self.username,
                                   self.scope,
                                   client_id=self.client_id,
                                   client_secret=self.client_secret,
                                   redirect_uri=redirect_uri)

        self.sp = spotipy.Spotify(auth=self.get_token())
        # self.playlist_id = "0RQmvqO5SVHbMJzPTY4efG"
        self.initial_time = datetime.datetime.now()
        self.number_track_in_playlist = 0
        self.playlist_number = 0
        self.trakts_id_list = []

        self.playlist_id = ""
        self.number_max_playlist = 9500
        self.number_max_request1 = 99
        self.number_max_request2 = 49
        # self.number_max_request2 = 5
        self.traks_json = []
        self.path_to_save = os.environ[
            'APPDATA'] + "/spotipyDatabaseFred/database.json"
        self.path_to_save_feature = os.environ[
            'APPDATA'] + "/spotipyDatabaseFred/database_feature.json"
        self.path_to_save_name = os.environ[
            'APPDATA'] + "/spotipyDatabaseFred/database_name.json"
        self.feature_list = []
        self.trakts_name_list = []
        self.album_list = []
        self.path_to_save_album = os.environ[
            'APPDATA'] + "/spotipyDatabaseFred/database_album.json"
        return

    def get_token(self):
        token_info = self.spo.get_cached_token()
        if token_info:
            access_token = token_info['access_token']
            return access_token
        else:
            print("error token : ", token_info)

    def taille_playlist(self):
        # playlist_list_id_to_delete = []
        offset = 0
        for i in range(0, 50):
            playlists = self.sp.user_playlists(self.username,
                                               limit=self.number_max_request2,
                                               offset=offset)
            offset += self.number_max_request2
            number_of_plalist = 0
            for playlist in playlists['items']:
                number_of_plalist += 1
                # if playlist['id'] in playlist_list_id:
                # print("error playlist_list_id deja unfollower")
                # print(playlist_list_id)
                # print(playlist['id'])
                # break
                # if re.search("AuN°[0-9].*", playlist['name']) or re.search(
                        # "feature :.*", playlist['name']):
                print("mark playlist to delete :", playlist['name'])
                self.playlist_list_id_to_delete.append(playlist['id'])
            if number_of_plalist < 49:
                break


    def mark_playlist_to_delete(self):
        self.playlist_list_id_to_delete = []
        offset = 0
        for i in range(0, 50):
            playlists = self.sp.user_playlists(self.username,
                                               limit=self.number_max_request2,
                                               offset=offset)
            offset += self.number_max_request2
            number_of_plalist = 0
            for playlist in playlists['items']:
                number_of_plalist += 1
                # if playlist['id'] in playlist_list_id:
                # print("error playlist_list_id deja unfollower")
                # print(playlist_list_id)
                # print(playlist['id'])
                # break
                if re.search("AuN°[0-9].*", playlist['name']) or re.search(
                        "feature.*", playlist['name']):
                    print("mark playlist to delete :", playlist['name'])
                    self.playlist_list_id_to_delete.append(playlist['id'])
            if number_of_plalist < 49:
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
        refreshed_token = cached_token['refresh_token']
        new_token = self.spo.refresh_access_token(refreshed_token)
        print("new token : ", new_token['access_token'])  # <--
        # also we need to specifically pass `auth=new_token['access_token']`
        self.sp = spotipy.Spotify(auth=new_token['access_token'])
        return new_token

    def get_artist(self, name):
        results = self.sp.search(q='artist:' + name, type='artist')
        items = results['artists']['items']
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
                    limit=self.number_max_request2, after=None)
            else:
                artist_followed = self.sp.current_user_followed_artists(
                    limit=self.number_max_request2, after=artist_id)
            for key in artist_followed['artists']['items']:
                artist_id = key['id']
                # print("fred = " + artist_id)
                # print(key['name'])
                artist = self.get_artist(key['name'])
                if (artist != None):
                    artist_list.append(artist)
                    print(key['name'])

        return artist_list

    def show_artist_albums(self, artist):
        albums = []
        results = self.sp.artist_albums(artist['id'], album_type='album')
        albums.extend(results['items'])
        while results['next']:
            results = self.sp.next(results)
            albums.extend(results['items'])
        logger.info('Total albums: %s', len(albums))
        unique = set()  # skip duplicate albums
        album_output = []
        for album in albums:
            name = album['name'].lower()
            if (name not in unique) and (name != None):
                logger.info('ALBUM: %s', name)
                unique.add(name)
                # self.show_album_tracks(album)
                album_output.append(album)
        self.album_list.extend(album_output)
        return album_output

    def audio_features_list(self):
        number_trak_boucle = 0
        list_key = []
        feature_list = []
        for key in self.trakts_id_list:
            number_trak_boucle += 1
            list_key.append(key)
            if number_trak_boucle == self.number_max_request1:
                feature_list.extend(self.sp.audio_features(list_key))
                number_trak_boucle = 0
                list_key.clear()
        # print("feature_list", feature_list)
        return feature_list

    def playlist_from_feature(self, feature_name, min_max):
        print("processing playlist : ", feature_name)
        feature_dico = {}
        for key in self.feature_list:
            if key != None:
                # print(key[feature_name])
                if key[feature_name] != None:
                    feature_dico[key['id']] = key[feature_name]
        # print(feature_dico)
        if feature_dico != {}:
            if min_max == True:
                playlist_name = "feature : " + feature_name
                feature_dico = sorted(feature_dico.items(), key=lambda kv: kv[1])
            else:
                playlist_name = "feature rev : " + feature_name
                feature_dico = sorted(feature_dico.items(),
                                      key=lambda kv: kv[1],
                                      reverse=True)
            b = [x[0] for x in feature_dico]
            # print("b=", b)
            self.add_list_of_trackts(b, 1, playlist_name)

    def show_album_tracks(self, album):
        tracks = []
        results = self.sp.album_tracks(album['id'])
        tracks.extend(results['items'])
        while results['next']:
            results = self.sp.next(results)
            if results['items'] != None:
                tracks.extend(results['items'])
        for i, track in enumerate(tracks):
            logger.info('%s. %s', i + 1, track['name'])
        return tracks

    def add_library_playlist(self):
        self.add_list_of_trackts(self.trakts_id_list, 30, "AuN°")
        spotifyInstance.playlist_from_feature("energy", True)
        spotifyInstance.playlist_from_feature("acousticness", True)
        spotifyInstance.playlist_from_feature("danceability", True)
        spotifyInstance.playlist_from_feature("instrumentalness", True)
        spotifyInstance.playlist_from_feature("liveness", True)
        spotifyInstance.playlist_from_feature("loudness", True)
        spotifyInstance.playlist_from_feature("speechiness", True)
        spotifyInstance.playlist_from_feature("valence", True)
        spotifyInstance.playlist_from_feature("tempo", True)

        spotifyInstance.playlist_from_feature("energy", False)
        spotifyInstance.playlist_from_feature("acousticness", False)
        spotifyInstance.playlist_from_feature("danceability", False)
        spotifyInstance.playlist_from_feature("instrumentalness", False)
        spotifyInstance.playlist_from_feature("liveness", False)
        spotifyInstance.playlist_from_feature("loudness", False)
        spotifyInstance.playlist_from_feature("speechiness", False)
        spotifyInstance.playlist_from_feature("valence", False)
        spotifyInstance.playlist_from_feature("tempo", False)

    def create_or_read_database(self):
        trakts = []
        if self.complete == True:
            logger.info("create database")
            artiste_list = self.get_artist_followed()
            for key in artiste_list:
                album = (self.show_artist_albums(key))
                for key in album:
                    self.calcul_time_token()
                    trakts = (self.show_album_tracks(key))
                    self.traks_json.extend(trakts)
                    self.add_trakts_id_to_list(trakts)
                    # self.add_trakts_name_to_list(trakts)

            self.save_tracks_database_to_file(self.album_list,
                                              self.path_to_save_album)
            self.save_tracks_database_to_file(self.trakts_name_list,
                                              self.path_to_save_name)
            self.save_tracks_database_to_file(self.traks_json,
                                              self.path_to_save)
            self.feature_list = self.audio_features_list()
            self.save_tracks_database_to_file(self.feature_list,
                                              self.path_to_save_feature)
        else:
            logger.info("use database processing")
            self.add_trakts_id_to_list(self.read_database(self.path_to_save))
            self.feature_list = self.read_database(self.path_to_save_feature)

    def save_tracks_database_to_file(self, traks, path_to_save):
        if not os.path.exists(os.path.dirname(path_to_save)):
            try:
                os.makedirs(os.path.dirname(path_to_save))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        print(path_to_save)
        with open(path_to_save, "w") as outfile:
            json.dump(traks, outfile)

    def read_database(self,file_to_read ):
        if not os.path.exists(os.path.dirname(file_to_read)):
            raise Exception(
                "database don t exist.launch complete process first")
        with open(file_to_read) as json_file:
            traks = json.load(json_file)
        return traks

    def user_playlist_add_tracks_error(self, list_9500_track, playlist_id):
        i=0
        while i < 500:
            i+=1
            try:
                # print(list_9500_track)
                self.sp.user_playlist_add_tracks(self.username, playlist_id,
                                                 list_9500_track)
                break
            except spotipy.client.SpotifyException as e:
                if (e.http_status == 429):
                    print(e.http_status)
                    time.sleep(1)
                    continue
                elif (e.http_status == 401):
                    self.refresh_token()
                    continue
                else:
                    print(e)
                    continue
                    # raise e

    def add_list_of_trackts(self, trakts_id, number_max_playlist_wanted,
                            playlist_base_name):
        logger.info("add_list_of_trackt")
        list_9500_track = []
        number_track_in_playlist = 0
        track_number_request = 0
        total_trakt = 0
        playlist_number = 1
        date = datetime.datetime.now().strftime("%m/%d/%Y")
        playlist_name = playlist_base_name + str(playlist_number) + " : " + str(
            date)
        playlist = self.sp.user_playlist_create(self.username, playlist_name)
        playlist_id = playlist['id']
        # print("traks_id", trakts_id)
        print("traks to add", len(trakts_id))
        for track in trakts_id:
            list_9500_track.append(track)
            track_number_request += 1
            number_track_in_playlist += 1
            total_trakt += 1
            # print("traks to add", len(trakts_id))
            # print("total trakt processed = ", total_trakt)
            if track_number_request == self.number_max_request1 or len(
                    trakts_id) == total_trakt:
                # logger.info("add traks to plalist : "+ list_9500_track)
                # print("add short list")
                # print("len list added", len(list_9500_track))
                # raise Exception()
                self.user_playlist_add_tracks_error(list_9500_track,
                                                    playlist_id)
                list_9500_track.clear()
                track_number_request = 0
            if number_track_in_playlist >= self.number_max_playlist:
                playlist_number += 1
                if playlist_number > number_max_playlist_wanted:
                    break
                playlist_name = playlist_base_name + str(
                    playlist_number) + " : " + str(date)

                print("add new plalist : " , playlist_name)
                playlist = self.sp.user_playlist_create(
                    self.username, playlist_name)
                playlist_id = playlist['id']
                number_track_in_playlist = 0

    def add_trakts_id_to_list(self, tracks):
        dico = {}
        dico2={}
        for track in tracks:
            dico[track['id']] = track['name']
        l = list(dico.items())
        random.shuffle(l)
        dico = dict(l)
        for key, value in dico.items():
          if value not in dico2.values():
            dico2[key] = value

        for key, value in dico2.items():
            self.trakts_id_list.append(key)
            self.trakts_name_list.append(value)

        self.trakts_id_list = list(dict.fromkeys(self.trakts_id_list))
        random.shuffle(self.trakts_id_list)
        print("len trakts_id_list : ", len(self.trakts_id_list))

    def add_argument(self):
        parser = argparse.ArgumentParser(
            description="give credential for spotify")
        parser.add_argument('--client_id',
                            required=True,
                            help='give \
                client id. see : https://developer.spotify.com/documentation/general/guides/app-settings/ '
                            )

        parser.add_argument('--client_secret',
                            required=True,
                            help='give \
                client id. see : https://developer.spotify.com/documentation/general/guides/app-settings/ '
                            )

        parser.add_argument('--username',
                            required=True,
                            help='give your \
        spotify username ')

        parser.add_argument(
            '--complete',
            action="store_true",
            help='rebuild complete database (don t reuse existing database)')

        args = parser.parse_args()
        # print(args.client_id)
        self.client_id = args.client_id
        self.client_secret = args.client_secret
        self.username = args.username
        self.complete = args.complete


if __name__ == '__main__':
    spotifyInstance = SpotifyInstance()
    spotifyInstance.mark_playlist_to_delete()
    spotifyInstance.create_or_read_database()
    spotifyInstance.add_library_playlist()
    spotifyInstance.delete_marked_playlist()
    # main()
