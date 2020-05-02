import datetime
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
        return

    def get_token(self):
        token_info = self.spo.get_cached_token()
        if token_info:
            access_token = token_info['access_token']
            return access_token
        else:
            print("error token : ", token_info)

    def delete_all_playlist(self):
        playlist_list_id = []
        for i in range(0, 50):
            playlists = self.sp.user_playlists(self.username, limit=50)
            for playlist in playlists['items']:
                if playlist['id'] in playlist_list_id:
                    print("error playlist_list_id deja unfollower")
                    print(playlist_list_id)
                    print(playlist['id'])
                    # break
                playlist_list_id.append(playlist['id'])
                print("deleting playlist :", playlist)
                print(
                    self.sp.user_playlist_unfollow(self.username,
                                                   playlist['id']))

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

    def create_playlist(self):
        date = datetime.datetime.now().strftime("%m/%d/%Y")
        self.playlist_number += 1
        playlist_name = "AuN°" + str(self.playlist_number) + ":" + str(date)
        logger.info("create new playlist  : " + playlist_name)
        playlist = self.sp.user_playlist_create(self.username, playlist_name)
        if self.playlist_number > 30:
            raise Exception(
                "error. number of plalist created is most as 30. stop for \
                    security")
        return playlist['id']

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
            # if i == 0:
                # artist_followed = self.sp.current_user_followed_artists(
                    # limit=3, after=None)
            # else:
                # artist_followed = self.sp.current_user_followed_artists(
                    # limit=3, after=artist_id)
        for i in range(0, 50):
            if i == 0:
                artist_followed = self.sp.current_user_followed_artists(
                    limit=50, after=None)
            else:
                artist_followed = self.sp.current_user_followed_artists(
                    limit=50, after=artist_id)
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
        return album_output

    def show_album_tracks(self, album):
        tracks = []
        results = self.sp.album_tracks(album['id'])
        tracks.extend(results['items'])
        while results['next']:
            results = self.sp.next(results)
            tracks.extend(results['items'])
        for i, track in enumerate(tracks):
            logger.info('%s. %s', i + 1, track['name'])
        return tracks

    def add_traks_to_playlist(self, tracks):
        for i, track in enumerate(tracks):
            logger.info('adding trackt %s. %s', i + 1, track['name'])
            print(track['id'])
            while True:
                try:
                    self.sp.user_playlist_add_tracks(self.username,
                                                     self.playlist_id,
                                                     [track['id']])
                    self.number_track_in_playlist += 1
                    print("number of trak in playlist : " +
                          str(self.number_track_in_playlist))
                    if self.number_track_in_playlist > self.number_max_playlist:
                        self.playlist_id = self.create_playlist()
                        self.number_track_in_playlist = 0
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
                        raise e
                        # break

    def add_library_playlist(self):
        self.playlist_id = self.create_playlist()
        artiste_list = self.get_artist_followed()
        trakts = []
        for key in artiste_list:
            album = (self.show_artist_albums(key))
            for key in album:
                self.calcul_time_token()
                trakts = (self.show_album_tracks(key))
                # self.add_traks_to_playlist(trakts)
                self.add_trakts_id_to_list(trakts)
        # logger.info("trakx_id_list : ", str(self.trakts_id_list)
        self.add_list_of_trackts(self.trakts_id_list)

    def user_playlist_add_tracks_error(self, list_9500_track):
        while True:
                    try:
                        self.sp.user_playlist_add_tracks(
                            self.username, self.playlist_id, list_9500_track)
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
                            raise e

    def add_list_of_trackts(self, trakts_id):
        list_9500_track = []
        number_track_in_playlist = 0
        track_number_request = 0
        for track in trakts_id:
            list_9500_track.append(track)
            track_number_request +=1
            number_track_in_playlist += 1
            if track_number_request == 99:
                self.user_playlist_add_tracks_error(list_9500_track)
                list_9500_track.clear()
                track_number_request = 0
            if number_track_in_playlist >= self.number_max_playlist:
                self.playlist_id = self.create_playlist()
                number_track_in_playlist = 0

    def add_trakts_id_to_list(self, tracks):
        for track in tracks:
            self.trakts_id_list.append(track['id'])
        self.trakts_id_list = random.choices(self.trakts_id_list, k=len(self.trakts_id_list))

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
        spotify username')

        args = parser.parse_args()
        # print(args.client_id)
        self.client_id = args.client_id
        self.client_secret = args.client_secret
        self.username = args.username


if __name__ == '__main__':
    spotifyInstance = SpotifyInstance()
    spotifyInstance.delete_all_playlist()
    spotifyInstance.add_library_playlist()
    # main()
