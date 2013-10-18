#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import subprocess as sub
import threading
import time


ART_LEN = 20
SONG_LEN = 25
PLAY_COLOR = "#00AAFF"
PAUSE_COLOR = "#000088"


def enum(**enums):
    return type('Enum', (), enums)

MPC_STATE = enum(UNKNOWN=0, STOPPED=1, PAUSED=2, PLAYING=3)


class Py3status:

    def __init__(self):
        self.lock = threading.Lock()

        # on the first call we can't wait until the song changes to return sth
        self.__read_mpd_status()

        self.thr = threading.Thread(target=self.__wait_for_mpd_event)
        self.thr.daemon = True
        self.thr.start()

    def show_current_song(self, json, i3statuscfg):
        """Main method that is actually executed by py3status.
           Shows song currently played/paused by mpd.
        """
        if not self.thr.is_alive():
            with open('/tmp/mpd_state', 'a') as f:
                f.write("mpd idle thread is dead at %s" % time.ctime(time.time()))
        response = {'full_text' : '', 'name' : 'mpdsong'}

        self.lock.acquire()
        if self.play_status != MPC_STATE.STOPPED:
            # no output needed when music is stopped
            self.__prep_output(response)
        self.lock.release()

        response['cached_until'] = time.time() 
        return (0, response)

    def kill(self):
        with open('/tmp/mpd_state', 'w') as f:
            f.write("trying to join mpd idle thread %s" % time.ctime(time.time()))
        self.thr.join()
        if not self.thr.is_alive():
            with open('/tmp/mpd_state', 'a') as f:
                f.write("joined mpd idle thread %s" % time.ctime(time.time()))

    def __cap(self, text, length):
        return text if len(text) <= length else text[0:length-3] + '...'

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
        self.lock.acquire()
        self.play_status = MPC_STATE.STOPPED
        self.current_song = "foo - bar"
        self.track_number = 0

        p = sub.Popen(args=['mpc'], stdin=sub.PIPE, stdout=sub.PIPE)
        mpc_out = p.communicate()[0].splitlines()

        if len(mpc_out) >= 2:
            status, rest = mpc_out[1].split(' ', 1)
            if status.startswith('[playing]'):
                self.play_status = MPC_STATE.PLAYING
            elif status.startswith('[paused]'):
                self.play_status = MPC_STATE.PAUSED
            self.track_number = rest.strip().split('/')[0][1:]
            self.current_song = mpc_out[0].strip()

        self.lock.release()

    def __wait_for_mpd_event(self):
        """Waits for next mpd event while blocking the calling thread."""
        while True:
            cmd = ['mpc', 'idle', 'player']
            p = sub.Popen(args=cmd, stdin=sub.PIPE, stdout=sub.PIPE)
            p.wait()
            with open('/tmp/mpd', 'a') as f:
                f.write("mpc triggered at: %s\n" % time.ctime(time.time()))
            if p.returncode == 0:
                self.__read_mpd_status()
            else:
                # this avoids heavy load should the network be unreachable
                sleep(1)


if __name__ == '__main__':
    p = Py3status()
    print(p.show_current_song(0, 1))
