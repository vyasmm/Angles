from __future__ import absolute_import, division, print_function, unicode_literals

from subprocess import call

import envoy
import os.path

def youtube_to_mkv(youtube_link, song_title, dir_):
    mkv_output = song_title + youtube_link[-11:] 
    output = os.path.join(dir_, mkv_output) 
    while not(os.path.exists(output)):
        call(["youtube-dl", "-f 'bestaudio", "-o", output, youtube_link])
        print("youtube-dl", "-f bestaudio", "-o", output, youtube_link)
    return mkv_output


def youtube_thumbnail(youtube_link):
    output = envoy.run("youtube-dl --get-thumbnail " + youtube_link)
    output_str = output.std_out
    return output_str


