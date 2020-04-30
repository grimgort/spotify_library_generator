import datetime
import re
import argparse
import logging
import spotipy
import time
import spotipy.oauth2 as oauth
from spotipy import util
# To access authorised Spotify data
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
client_id = "a74e9479f7164cbe94a85f1d0956e67f"
client_secret = "6b80acbbef46465ea4aed39efc28b5ee"
username = "grimgort"
redirect_uri = 'http://localhost:9999'

LOG_FILENAME = 'logging_rotatingfile_example.out'
logger = logging.getLogger('examples.artist_discography')
logger.setLevel(logging.DEBUG)
logging.basicConfig(filename='spotilog.txt', level='INFO')


class SpotifyInstance:
    def __init__(self):
        self.scope = 'user-follow-read playlist-modify-public playlist-modify-private'
        self.spo = oauth.SpotifyOAuth(client_id=client_id,
                                      client_secret=client_secret,
                                      redirect_uri=redirect_uri,
                                      scope=self.scope,
                                      cache_path=".cache-{}".format(username))

        self.sp = spotipy.Spotify(auth=self.get_token())
        # self.playlist_id = "0RQmvqO5SVHbMJzPTY4efG"
        self.initial_time = datetime.datetime.now()
        self.number_track_in_playlist = 0
        self.playlist_id = self.create_playlist()
        return

    def calcul_time_token(self):
        time = datetime.datetime.now() - self.initial_time
        print("time = " ,time)
        if time >= datetime.timedelta(0,0,0,0,15,0,0) :
            print("token refresh")
            self.refresh_token()
            self.initial_time = datetime.datetime.now() 
        return



    def get_token(self):
        token_info = self.spo.get_cached_token()
        if token_info:
            access_token = token_info['access_token']
            return access_token
        # else:
        # auth = self.spo.get_authorize_url()
        # print(auth)
        # auth_url = input('Click the link above and copy and paste the url here: ')
        # _re_auth = re.findall(_auth_finder, auth_url)
        # access_token = self.spo.get_access_token(_re_auth[0])
        # return access_token

    # def refresh_token(self):
    # cached_token = self.spo.get_cached_token()
    # is_it_expired = self.spo.is_token_expired(cached_token)
    # if is_it_expired is True:
    # refreshed_token = cached_token['refresh_token']
    # new_token = self.spo.refresh_access_token(refreshed_token)
    # self.sp = spotipy.Spotify(auth=new_token)
    # return new_token

    def refresh_token(self):
        cached_token = self.spo.get_cached_token()
        print("token expire = ",self.spo.is_token_expired(cached_token))
        refreshed_token = cached_token['refresh_token']
        new_token = self.spo.refresh_access_token(refreshed_token)
        print("new token : ",  new_token['access_token'])  # <--
        # also we need to specifically pass `auth=new_token['access_token']`
        self.sp = spotipy.Spotify(auth=new_token['access_token'])
        return new_token

    def create_playlist(self):
        date = datetime.datetime.now()
        playlist_name = "playlistDu" + str(date)
        playlist = self.sp.user_playlist_create(username, playlist_name)
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

        for i in range(0, 50):
            # while True:
                # try:
                    # self.sp.user_playlist_add_tracks('grimgort', playlist_id, [track['id']])
            if i == 0:
                artist_followed = self.sp.current_user_followed_artists(
                    limit=50, after=None)
            else:
                artist_followed = self.sp.current_user_followed_artists(
                    limit=50, after=artist_id)
            # break
        # for i in range(0, 1):
            # while True:
                # try:
                    # # self.sp.user_playlist_add_tracks('grimgort', playlist_id, [track['id']])
                    # if i == 0:
                        # artist_followed = self.sp.current_user_followed_artists(
                            # limit=2, after=None)
                    # else:
                        # artist_followed = self.sp.current_user_followed_artists(
                            # limit=2, after=artist_id)
                    # break
                # except Exception as e:
                    # if (e.http_status == 429):
                        # print(e.http_status)
                        # time.sleep(1)
                        # continue
                    # elif (e.http_status == 503):
                        # self.refresh_token
                        # continue
            for key in artist_followed['artists']['items']:
                artist_id = key['id']
                # print("fred = " + artist_id)
                # print(key['name'])
                artist = self.get_artist(key['name'])
                if (artist != None):
                    artist_list.append(artist)
                    print(key['name'])
                # y += 1
                # print(y)
                # show_artist(artist)
                # show_artist_albums(artist, playlist_id, sp)

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
        album_output =[]
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
        # print(album['id'])
        results = self.sp.album_tracks(album['id'])
        tracks.extend(results['items'])
        while results['next']:
            results = self.sp.next(results)
            tracks.extend(results['items'])
            # logger.info('trakt: %s', results['items'])
        for i, track in enumerate(tracks):
            logger.info('%s. %s', i+1, track['name'])
        return tracks

    def add_traks_to_playlist(self, tracks):
        for i, track in enumerate(tracks):
            logger.info('adding trackt %s. %s', i + 1, track['name'])
            print
            (track['id'])
            # self.refresh_token()
            # time.sleep(0.2)
            # for i in range(0,100):
            while True:
                try:
                    self.sp.user_playlist_add_tracks('grimgort',
                                                     self.playlist_id,
                                                     [track['id']])
                    self.number_track_in_playlist += 1
                    if self.number_track_in_playlist >9900:
                        self.playlist_id = self.create_playlist()
                    break
                except spotipy.client.SpotifyException as e:
                    if (e.http_status == 429):
                        print(e.http_status)
                        time.sleep(1)
                        continue
                    elif (e.http_status == 401):
                        self.refresh_token()
                        continue
                    else :
                        print(e)


    def add_library_playlist(self):
        artiste_list = self.get_artist_followed()
        # album = []
        trakts = []
        # i=0
        for key in artiste_list:
            # test = (self.show_artist_albums(key))
            # print(test.type)
            # test2 = test['id']
            album=(self.show_artist_albums(key))
            for key in album:
                self.calcul_time_token() 
                # trakts.append(self.show_album_tracks(key))
                trakts = (self.show_album_tracks(key))
                # for track in trakts:
                # print(track)
                # self.sp.user_playlist_add_tracks('grimgort', self.playlist_id, track['id'])
                # self.add_track
                self.add_traks_to_playlist(trakts)
        # for album_track in trakts:
        # print(album_track)
        # for track in album_track:
        # print(track)
        # while True:
        # try:
        # self.sp.user_playlist_add_tracks('grimgort', self.playlist_id, track['id'])
        # logger.info('%s. %s', i + 1, track['name'])
        # break
        # except spotipy.client.SpotifyException as e:
        # if (e.http_status == 429):
        # print(e.http_status)
        # time.sleep(1)
        # continue
        # elif (e.http_status == 503):
        # self.refresh_token
        # continue
        # return

if __name__ == '__main__':
    spotifyInstance = SpotifyInstance()
    spotifyInstance.add_library_playlist()
    # main()
