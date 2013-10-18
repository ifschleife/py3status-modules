#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import subprocess as sub


ART_LEN = 20
SONG_LEN = 25
PLAY_COLOR = "#00AAFF"
PAUSE_COLOR = "#000088"


def cap(text, length):
    return text if len(text) <= length else text[0:length-3] + '...'


class Py3status:

    def show_current_song(self, json, i3statuscfg):
        """Shows song currently played/paused by mpd."""
        response = {'full_text' : '', 'name' : 'mpdsong'}

        cmd = ['mpc', 'current']
        p = sub.Popen(args=cmd, stdin=sub.PIPE, stdout=sub.PIPE)
        out = p.communicate()

        title = out[0].strip()
        artist, song = title.split(' - ')

        cmd = ['mpc']
        p = sub.Popen(args=cmd, stdin=sub.PIPE, stdout=sub.PIPE)
        out = p.communicate()
        out = out[0].splitlines()

        out = out[1].split(' ')
        if out[0] == '[playing]':
            response.update({'color' : PLAY_COLOR})
            number = out[1].split('/')[0][1:]
        else:
            response.update({'color' : PAUSE_COLOR})
            number = out[2].split('/')[0][1:]

        # the space is appended bc some characters overlap with the i3 divider
        # otherwise, such as a ")"
        response['full_text'] = "%s. %s - %s " % (number,
                                                  cap(artist, ART_LEN),
                                                  cap(song, SONG_LEN))

        return (0, response)

if __name__ == '__main__':
    p = Py3status()
    print(p.show_current_song(0, 1))
