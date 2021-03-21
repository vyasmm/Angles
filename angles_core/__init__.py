from __future__ import absolute_import, division, print_function, unicode_literals

import datetime
import os

from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename

from angles_core import youtube_downloads as convert, alignment_by_row_channels

UPLOAD_FOLDER = "uploads/"
ALLOWED_EXTENSIONS = {"mkv"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1] in ALLOWED_EXTENSIONS


def _process_file(new_title, url):
    if url:
        new_filename = convert.youtube_to_mkv(url, new_title, UPLOAD_FOLDER)
        new_youtube_url = "https://www.youtube.com/embed/" + url[-11:]
        new_thumbnail = convert.youtube_thumbnail(url)
    else:
        raise ValueError("Specify either a YouTube link or a file to upload")

    return new_filename, new_thumbnail, new_youtube_url



def _post():

    new_title = request.form.get("title")

    url1 = request.form.get("url1").split("&")[0]
    if url1:
        filename1, thumbnail1, new_url1 = _process_file(new_title, url1)


    url2 = request.form.get("url2").split("&")[0]
    if url2:
        filename2, thumbnail2, new_url2 = _process_file(new_title, url2)

    url3 = request.form.get("url3").split("&")[0]
    if url3:
        filename3, thumbnail3, new_url3 = _process_file(new_title, url3)

    url4 = request.form.get("url4").split("&")[0]
    if url4:
        filename4, thumbnail4, new_url4 = _process_file(new_title, url4)
    
    #print(str(delay))
    if url3:
        l1 = alignment_by_row_channels.align(filename1, filename2, UPLOAD_FOLDER).split("&t=")
        d12 = float(l1[1].split("&")[0])
        d21 = float(l1[2].split("&")[0])
        if d21 == 0 :
            l2 = alignment_by_row_channels.align(filename2, filename3, UPLOAD_FOLDER).split("&t=")
            d23 = float(l2[1].split("&")[0])
            d32 = float(l2[2].split("&")[0])
            if d23 == 0:
               v2 = 0
               v3 = d32
               v1 = d12
            else:
                v3 = 0
                v2 = d23
                v1 = v2+d12
        else: 
            l3 = alignment_by_row_channels.align(filename3, filename1, UPLOAD_FOLDER).split("&t=")
            d31 = float(l3[1].split("&")[0])
            d13 = float(l3[2].split("&")[0])
            if d13 == 0:
               v1 = 0
               v3 = d31
               v2 = d21
            else:
                v3 = 0
                v1 = d13
                v2 = v1+d21

        if url4:
            if v1 == 0:
                l4 = alignment_by_row_channels.align(filename4, filename1, UPLOAD_FOLDER).split("&t=")
                d41= float(l4[1].split("&")[0])
                d14= float(l4[2].split("&")[0])
                if d14 == 0:
                    v1 = 0
                    v4 = d41
                else:
                    v4 = 0
                    v1 = d14
                    v2 += v1
                    v3 += v1
            
            elif v2 == 0:
                l4 = alignment_by_row_channels.align(filename4, filename2, UPLOAD_FOLDER).split("&t=")
                d42= float(l4[1].split("&")[0])
                d24= float(l4[2].split("&")[0])
                if d24 == 0:
                    v2 = 0
                    v4 = d42
                else:
                    v4 = 0
                    v2 = d24
                    v1 += v2
                    v3 += v2
            
            else:
                l4 = alignment_by_row_channels.align(filename4, filename3, UPLOAD_FOLDER).split("&t=")
                d43= float(l4[1].split("&")[0])
                d34= float(l4[2].split("&")[0])
                if d34 == 0:
                    v3 = 0
                    v4 = d43
                else:
                    v4 = 0
                    v3 = d34
                    v2 += v3
                    v1 += v3

            print(v1,v2,v3,v4)
            #from angles_core import url_redirect as redirect
            #print("Loading the videos in Browser")
            link = "https://viewsync.net/watch?v="+url1[-11:]+"&t="+str(v1)+"&v="+url2[-11:]+"&t="+str(v2)+"&v="+url3[-11:]+"&t="+str(v3)+"&v="+url4[-11:]+"&t="+str(v4)+"&mode=solo" 

        else:
            print(v1,v2,v3)
            #from angles_core import url_redirect as redirect
            #print("Loading the videos in Browser")
            link = "https://viewsync.net/watch?v="+url1[-11:]+"&t="+str(v1)+"&v="+url2[-11:]+"&t="+str(v2)+"&v="+url3[-11:]+"&t="+str(v3)+"&mode=solo" 
            
    else:
        #print("Loading the videos in Browser")
        link = alignment_by_row_channels.align(filename1, filename2, UPLOAD_FOLDER)
    return redirect(link)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        return _post()
    else:
        
        return render_template("index.html")

