# -*- coding: utf-8 -*-
#------------------------------------------------------------
# PalcoTV - XBMC Add-on by Juarrox (juarrox@gmail.com)
# Version 0.2.92 (18.07.2014)
#------------------------------------------------------------
# License: GPL (http://www.gnu.org/licenses/gpl-3.0.html)
# Librerías Plugintools por Jesús (www.mimediacenter.info)


import os
import sys
import urllib
import urllib2
import re
import shutil
import zipfile

import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin

import plugintools


home = xbmc.translatePath(os.path.join('special://home/addons/plugin.video.palcotv/', ''))
tools = xbmc.translatePath(os.path.join('special://home/addons/plugin.video.palcotv/resources/tools', ''))
addons = xbmc.translatePath(os.path.join('special://home/addons/', ''))
resources = xbmc.translatePath(os.path.join('special://home/addons/plugin.video.palcotv/resources', ''))
art = xbmc.translatePath(os.path.join('special://home/addons/plugin.video.palcotv/art', ''))
tmp = xbmc.translatePath(os.path.join('special://home/addons/plugin.video.palcotv/tmp', ''))
playlists = xbmc.translatePath(os.path.join('special://home/addons/playlists', ''))

icon = art + 'icon.png'
fanart = 'fanart.jpg'



def allmyvideos(params):
    plugintools.log("[PalcoTV-0.3.0].allmyvideos " + repr(params))

    url = params.get("url")
    url = url.split("/")
    url_fixed = 'http://www.allmyvideos.net/' +  'embed-' + url[3] +  '.html'
    plugintools.log("url_fixed= "+url_fixed)

    request_headers=[]
    request_headers.append(["User-Agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.65 Safari/537.31"])
    body,response_headers = plugintools.read_body_and_headers(url_fixed, headers=request_headers)
    plugintools.log("data= "+body)

    r = re.findall('"file" : "(.+?)"', body)
    for entry in r:
        plugintools.log("vamos= "+entry)
        if entry.endswith("mp4?v2"):
            url = entry
            params["url"]=url
            plugintools.log("url= "+url)
            plugintools.play_resolved_url(url)
            xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('PalcoTV', "Resolviendo enlace...", 3 , art+'icon.png'))


def streamcloud(params):
    plugintools.log("[PalcoTV-0.3.0].streamcloud " + repr(params))

    url = params.get("url")

    request_headers=[]
    request_headers.append(["User-Agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.65 Safari/537.31"])
    body,response_headers = plugintools.read_body_and_headers(url, headers=request_headers)
    plugintools.log("data= "+body)

    # Barra de progreso para la espera de 10 segundos
    progreso = xbmcgui.DialogProgress()
    progreso.create("PalcoTV", "Abriendo Streamcloud..." , url )

    i = 13000
    j = 0
    percent = 0
    while j <= 13000 :
        percent = ((j + ( 13000 / 10.0 )) / i)*100
        xbmc.sleep(i/10)  # 10% = 1,3 segundos
        j = j + ( 13000 / 10.0 )
        msg = "Espera unos segundos, por favor... "
        percent = int(round(percent))
        print percent
        progreso.update(percent, "" , msg, "")
        

    progreso.close()
    
    media_url = plugintools.find_single_match(body , 'file\: "([^"]+)"')
    
    if media_url == "":
        op = plugintools.find_single_match(body,'<input type="hidden" name="op" value="([^"]+)"')
        usr_login = ""
        id = plugintools.find_single_match(body,'<input type="hidden" name="id" value="([^"]+)"')
        fname = plugintools.find_single_match(body,'<input type="hidden" name="fname" value="([^"]+)"')
        referer = plugintools.find_single_match(body,'<input type="hidden" name="referer" value="([^"]*)"')
        hashstring = plugintools.find_single_match(body,'<input type="hidden" name="hash" value="([^"]*)"')
        imhuman = plugintools.find_single_match(body,'<input type="submit" name="imhuman".*?value="([^"]+)">').replace(" ","+")

        post = "op="+op+"&usr_login="+usr_login+"&id="+id+"&fname="+fname+"&referer="+referer+"&hash="+hashstring+"&imhuman="+imhuman
        request_headers.append(["Referer",url])
        body,response_headers = plugintools.read_body_and_headers(url, post=post, headers=request_headers)
        plugintools.log("data= "+body)
        

        # Extrae la URL
        media_url = plugintools.find_single_match( body , 'file\: "([^"]+)"' )
        plugintools.log("media_url= "+media_url)
        plugintools.play_resolved_url(media_url)

        if 'id="justanotice"' in body:
            plugintools.log("[streamcloud.py] data="+body)
            plugintools.log("[streamcloud.py] Ha saltado el detector de adblock")
            return -1

  

def playedto(params):
    plugintools.log("[PalcoTV-0.3.0].playedto " + repr(params))

    url = params.get("url")
    url = url.split("/")
    url_fixed = "http://played.to/embed-" + url[3] +  "-640x360.html"
    plugintools.log("url_fixed= "+url_fixed)

    request_headers=[]
    request_headers.append(["User-Agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.65 Safari/537.31"])
    body,response_headers = plugintools.read_body_and_headers(url_fixed, headers=request_headers)
    plugintools.log("data= "+body)

    r = re.findall('file(.+?)\n', body)
    
    for entry in r:
        
        entry = entry.replace('",', "")
        entry = entry.replace('"', "")
        entry = entry.replace(': ', "")
        entry = entry.strip()
        plugintools.log("vamos= "+entry)
        
        if entry.endswith("flv"):
            plugintools.play_resolved_url(entry)
            xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('PalcoTV', "Resolviendo enlace...", 3 , art+'icon.png'))            
            params["url"]=entry
            plugintools.log("URL= "+entry)



def vidspot(params):
    plugintools.log("[PalcoTV-0.3.0].vidspot " + repr(params))

    url = params.get("url")
    url = url.split("/")
    url_fixed = 'http://www.vidspot.net/' +  'embed-' + url[3] +  '.html'
    plugintools.log("url_fixed= "+url_fixed)

    request_headers=[]
    request_headers.append(["User-Agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.65 Safari/537.31"])
    body,response_headers = plugintools.read_body_and_headers(url_fixed, headers=request_headers)
    plugintools.log("data= "+body)

    r = re.findall('"file" : "(.+?)"', body)
    for entry in r:
        plugintools.log("vamos= "+entry)
        if entry.endswith("mp4?v2"):
            url = entry
            params["url"]=url
            plugintools.log("url= "+url)
            plugintools.play_resolved_url(url)
            xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('PalcoTV', "Resolviendo enlace...", 3 , art+'icon.png'))


def vk(params):
    plugintools.log("[PalcoTV-0.3.0].vk " + repr(params))

    # http://vk.com/video_ext.php?oid=238208017&id=169663934&hash=1fc3ef827b751943&hd=1

    data = plugintools.read(params.get("url"))
    data = data.replace("amp;", "")
    
    if "This video has been removed from public access" in data:
        xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('PalcoTV', "El archivo ya no está disponible", 3 , art+'icon.png'))
    else:
        match = plugintools.find_single_match(data, '<param name="flashvars"(.*?)</param>')
        plugintools.log("match= "+match)
        matches = plugintools.find_multiple_matches(match, 'vkid(.*?)&')
        for entry in matches:
            plugintools.log("match= "+entry)

        video_host = plugintools.find_single_match(data, 'var video_host = \'(.*?)\';')
        print 'video_host',video_host
        video_uid = plugintools.find_single_match(data, 'var video_uid = \'(.*?)\';')
        print 'video_uid',video_uid        
        video_vtag = plugintools.find_single_match(data, 'var video_vtag = \'(.*?)\';')
        print 'video_vtag',video_vtag        
        video_no_flv = plugintools.find_single_match(data, 'var video_no_flv = \'(.*?)\';')
        print 'video_no_flv',video_no_flv        
        video_max_hd = plugintools.find_single_match(data, 'var video_max_hd = \'(.*?)\';')
        print 'video_max_hd',video_max_hd

        if video_no_flv.strip() == "0" and video_uid != "0":
            media = 'flv'

        url_sintax = video_host + video_uid + '/video/' + video_vtag
        plugintools.log("url_sintax= "+url_sintax)

        # Control para el caso en que no se encuentren los parámetros por "Acceso prohibido o restringido"
        if url_sintax == "/video":
            xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('PalcoTV', "El archivo ya no está disponible", 3 , art+'icon.png'))
        else:            
            url_1 = url_sintax + '.240.mp4'
            url_extended_1 = plugintools.find_single_match(match, 'url240=(.*?)\&')
            url_2 = url_sintax + '.360.mp4'
            url_extended_2 = plugintools.find_single_match(match, 'url360=(.*?)\&')
            url_3 = url_sintax + '.480.mp4'
            url_extended_3 = plugintools.find_single_match(match, 'url480=(.*?)\&')
            url_4 = url_sintax + '.720.mp4'
            url_extended_4 = plugintools.find_single_match(match, 'url720=(.*?)\&')

            video_urls = [url_extended_1, url_extended_2, url_extended_3, url_extended_4]
            print video_urls
            
            dialog_vk = xbmcgui.Dialog()
            selector = ""        
            
            if video_max_hd == "0":
                selector = dialog_vk.select('PalcoTV', ['240'])

            if video_max_hd == "1":
                selector = dialog_vk.select('PalcoTV', ['240', '360'])

            if video_max_hd == "2":
                selector = dialog_vk.select('PalcoTV', ['240', '360', '480'])

            if video_max_hd == "3":
                selector = dialog_vk.select('PalcoTV', ['240', '360', '480', '720'])                      

            i = 0
            while i<= video_max_hd :
                if selector == i:
                    plugintools.log("URL_vk= "+video_urls[i])
                    url = video_urls[i]
                    if selector == "":
                        xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('PalcoTV', "El archivo ya no está disponible", 3 , art+'icon.png'))
                    else:
                        plugintools.play_resolved_url(url)

                i = i + 1


def nowvideo(params):
    plugintools.log("[PalcoTV-0.3.0].nowvideo " + repr(params))

    data = plugintools.read(params.get("url"))
    #data = data.replace("amp;", "")
    
    if "The file is being converted" in data:
        xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('PalcoTV', "El archivo está en proceso", 3 , art+'icon.png'))
    elif "no longer exists" in data:
        xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('PalcoTV', "El archivo ha sido borrado", 3 , art+'icon.png'))        
    else:
        #plugintools.log("data= "+data)
        domain = plugintools.find_single_match(data, 'flashvars.domain="([^"]+)')
        video_id = plugintools.find_single_match(data, 'flashvars.file="([^"]+)')
        filekey = plugintools.find_single_match(data, 'flashvars.filekey=([^;]+)')

        # En la página nos da el token de esta forma (siendo fkzd el filekey): var fkzd="83.47.1.12-8d68210314d70fb6506817762b0d495e";

        token_txt = 'var '+filekey
        #plugintools.log("token_txt= "+token_txt)
        token = plugintools.find_single_match(data, filekey+'=\"([^"]+)')
        token = token.replace(".","%2E").replace("-","%2D")
        
        #plugintools.log("domain= "+domain)   
        #plugintools.log("video_id= "+video_id)
        #plugintools.log("filekey= "+filekey)
        #plugintools.log("token= "+token)
        
        if video_id == "":
            xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('PalcoTV', "Error!", 3 , art+'icon.png'))
        else:
            #http://www.nowvideo.sx/api/player.api.php?user=undefined&pass=undefined&cid3=undefined&numOfErrors=0&cid2=undefined&key=83%2E47%2E1%2E12%2D8d68210314d70fb6506817762b0d495e&file=b5c8c44fc706f&cid=1
            url = 'http://www.nowvideo.sx/api/player.api.php?user=undefined&pass=undefined&cid3=undefined&numOfErrors=0&cid2=undefined&key=' + token + '&file=' + video_id + '&cid=1'

            # Vamos a lanzar una petición HTTP de esa URL
            referer = 'http://www.nowvideo.sx/video/b5c8c44fc706f'
            request_headers=[]
            request_headers.append(["User-Agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.65 Safari/537.31"])
            request_headers.append(["Referer",referer])
            body,response_headers = plugintools.read_body_and_headers(url, headers=request_headers)
            # plugintools.log("data= "+body)
            # body= url=http://s173.coolcdn.ch/dl/04318aa973a3320b8ced6734f0c20da3/5440513e/ffe369cb0656c0b8de31f6ef353bcff192.flv&title=The.Black.Rider.Revelation.Road.2014.DVDRip.X264.AC3PLAYNOW.mkv%26asdasdas&site_url=http://www.nowvideo.sx/video/b5c8c44fc706f&seekparm=&enablelimit=0

            body = body.replace("url=", "")
            body = body.split("&")

            if len(body) >= 0:
                print 'body',body
                url = body[0]
                plugintools.play_resolved_url(url)
                xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('PalcoTV', "Cargando vídeo...", 1 , art+'icon.png'))
            else:
                xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('PalcoTV', "Error!", 3 , art+'icon.png'))                

         
''' En el navegador...

        flashvars.domain="http://www.nowvideo.sx";
        flashvars.file="b5c8c44fc706f";
        flashvars.filekey=fkzd;
        flashvars.advURL="0";
        flashvars.autoplay="false";
        flashvars.cid="1";

'''


def tumi(params):
    plugintools.log("[PalcoTV[0.3.0].Tumi "+repr(params))

    data = plugintools.read(params.get("url"))
    
    if "Video is processing now" in data:
        xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('PalcoTV', "El archivo está en proceso", 3 , art+'icon.png'))       
    else:
        # Vamos a buscar el ID de la página embebida
        matches = plugintools.find_multiple_matches(data, 'add_my_acc=(.*?)\"')
        for entry in matches:
            print 'match',entry
            # http://tumi.tv/embed-i9l4mr7jph1a.html
            url = 'http://tumi.tv/embed-' + entry + '.html'
            
            # Petición HTTP de esa URL
            request_headers=[]
            request_headers.append(["User-Agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.65 Safari/537.31"])
            request_headers.append(["Referer",params.get("url")])
            body,response_headers = plugintools.read_body_and_headers(url, headers=request_headers)
            plugintools.log("body= "+body)
            video_url= plugintools.find_single_match(body, 'file\: \"(.*?)\"')
            plugintools.log("video_url= "+video_url)
            plugintools.add_item(action="play", title= "hola" , url = video_url , folder = False , isPlayable = True)
            plugintools.play_resolved_url(video_url)

            
