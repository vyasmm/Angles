








def url_redirect(seconds, link1, link2):
    url = "https://viewsync.net/watch?v=" 
    if seconds > 0:
        l1 = link1 + "&t=0" 
        l2 = link2 + "&t=" + str(seconds)
        url = url + l1 + "&v=" + l2 + "&mode=solo"
    
    else:
        l1 = link1 + "&t=" + str(abs(seconds))
        l2 = link2 + "&t=0"
        url = url + l1 + "&v=" + l2 + "&mode=solo"

    return url

def redirect_url():
    url = "https://viewsync.net/watch?v="
    return url