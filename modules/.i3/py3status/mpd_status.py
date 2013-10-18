#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import subprocess as sub
import threading
import time

from mpd import MPDClient, ConnectionError

MPD_HOST = "@HOST@"
MPD_PORT = "@PORT@"
MPD_PASS = "@PASSWORD@"

ART_LEN = 20
SONG_LEN = 25
PLAY_COLOR = "#00AAFF"
PAUSE_COLOR = "#000088"


def enum(**enums):
    return type('Enum', (), enums)

MPC_STATE = enum(UNKNOWN=0, STOPPED=1, PAUSED=2, PLAYING=3)


class Py3status:

    def __init__(self):
        self.mpd_client = MPDClient()
        self.__connect_to_mpd()

    def show_current_song(self, json, i3statuscfg):
        """Main method that is actually executed by py3status.
           Shows song currently played/paused by mpd.
        """
        response = {'full_text' : '', 'name' : 'mpdsong'}

        self.__read_mpd_status()

        if self.play_status != MPC_STATE.STOPPED:
            # no output needed when music is stopped
            self.__prep_output(response)

        response['cached_until'] = time.time() 
        return (0, response)

    def __cap(self, text, length):
        return text if len(text) <= length else text[0:length-3] + '...'

    def __connect_to_mpd(self):
        self.mpd_client.connect(MPD_HOST, MPD_PORT)
        self.mpd_client.password(MPD_PASS)

    def __prep_output(self, response):
        artist, song = self.current_song.split(' - ')

        if self.play_status == MPC_STATE.PLAYING:
            response.update({'color' : PLAY_COLOR})
        elif self.play_status == MPC_STATE.PAUSED:
            response.update({'color' : PAUSE_COLOR})

        # the space is appended because otherwise some characters overlap with
        # the i3 divider, such as a ")"
        response['full_text'] = "%s. %s - %s " % (self.track_number,
                                                  self.__cap(artist, ART_LEN),
                                                  self.__cap(song, SONG_LEN))

    def __read_mpd_status(self):
        """Reads song currently played by mpd (if any)."""
        self.play_status = MPC_STATE.STOPPED
        self.current_song = "foo - bar"
        self.track_number = 0

        try:
            status = self.mpd_client.status()
        except ConnectionError:
            self.__connect_to_mpd()
            status = self.mpd_client.status()

        if status['state'] == 'play':
            self.play_status = MPC_STATE.PLAYING
        elif status['state'] == 'pause':
            self.play_status = MPC_STATE.PAUSED

        song = self.mpd_client.currentsong()
        self.track_number = song['track']
        self.current_song = "%s - %s" % (song['artist'], song['title'])


if __name__ == '__main__':
    p = Py3status()
    print(p.show_current_song(0, 1))
