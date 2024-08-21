from dotenv import load_dotenv
import os
import base64
from requests import get, post
import json
import subprocess
import yt_dlp as youtube_dl
import time

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

spotify_id = "1lCixp10Q7jULw1l"  # ← Nahi den playlista lortu

# Tokena lortzen da
def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}  # ← zein formatu eduki behar duen.

    result = post(url, headers=headers, data=data)  # ← Hemen jasotzen dugu bidali egin duguna eta honen erantzuna gorde egiten da bertako bariablean.
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

# Tokenaren bidez gomendatzen du
def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

token = get_token()

# Lista de reproduccióna lortzen da
def obtein_Playlist(token, playlist):
    url = f"https://api.spotify.com/v1/playlists/{playlist}"

    headers = get_auth_header(token)

    result = get(url, headers=headers)
    json_result = json.loads(result.content)

    print(json_result["name"])
    print(json_result["images"][0]["url"])

    name = json_result['name']

    karpeta = f"./list/{name}"
    try:
        os.stat(karpeta)
    except:
        os.mkdir(karpeta)

# Playlista lortuko dugu
def obtein_Playlist_item(token, spotify_id, buelta):
    url = f"https://api.spotify.com/v1/playlists/{spotify_id}/tracks"

    while url:
        headers = get_auth_header(token)
        result = get(url, headers=headers)
        json_result = json.loads(result.content)

        for i, item in enumerate(json_result.get("items", [])):
            if item and item.get("track"):
                track_id = item["track"].get("id", "N/A")
                track_name = item["track"].get("name", "N/A")

                artists = item["track"].get("artists", [])
                artist_names = ", ".join(artist.get("name", "N/A") for artist in artists)
                
                ##print(track_name)
                #print(artist_names)

                mp3Download(track_name, artist_names)

        # Pagina eguneko lerroa eguneratu
        url = json_result.get("next")
        buelta += 100

    print('¡Descarga finalizada! Vaya a su carpeta de música.')

#MP3 hau YT erabiliz deskargatzeko
def mp3Download(song_name, artist_name):
    time.sleep(1)
    #YouTube erakusteko bilaketa egin
    search_url = f"ytsearch:{song_name+' '+artist_name}"
    ydl_opts = {
        'format': 'bestaudio/best',  # Formatura gehien onena
        'noplaylist': True,  # Erreproduktore-zerrenda ez
        'quiet': True,  # Isil
    }

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(search_url, download=False)
            if 'entries' in info_dict:
                video_info = info_dict['entries'][0]
            else:
                print(f"No se encontró ningún video para '{song_name}' en YouTube.")
                return

        output_dir = os.path.join(os.getcwd(), 'Musika')
        os.makedirs(output_dir, exist_ok=True)

        filename = os.path.join(output_dir, f"{video_info['title']}.mp3")
        options = {
            'format': 'bestaudio/best',
            'keepvideo': False,
            'outtmpl': filename,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        }

        with youtube_dl.YoutubeDL(options) as ydl:
            ydl.download([video_info['webpage_url']])

        subprocess.call(["open", filename])  #Irekiko musika fitxategia

    except Exception as e:
        print(f"Error al descargar '{song_name}' desde YouTube: {str(e)}")
        with open('errores.txt', 'a') as f:
            f.write(f"{song_name}\n")

#Dena ondo pasa arte
obtein_Playlist(token, spotify_id)
obtein_Playlist_item(token, spotify_id, 0)
