from datetime import datetime
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

BILLBOARD_URL = "https://www.billboard.com/charts/hot-100/"
SPOTIFY_ID = os.environ.get("CLIENT_ID")
SPOTIFY_SECRET = os.environ.get("CLIENT_SECRET")
SPOTIFY_USER = os.environ.get("USERNAME")


sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    scope="playlist-modify-private",
    redirect_uri="http://localhost:8888/callback",
    client_id=SPOTIFY_ID,
    client_secret=SPOTIFY_SECRET,
    show_dialog=True,
    cache_path="toxen.txt",
    username=SPOTIFY_USER
    )
)

user_id = sp.current_user()["id"]

music_off = True

while music_off:
    music_prompt = input("What year would you like to travel to? Enter your answer in this format YYYY-MM-DD:  ")
    try:
        datetime.strptime(music_prompt, "%Y-%m-%d")
        music_off = False
    except ValueError:
        print("The provided dates were improperly formatted, please try again\n")


response = requests.get(url=BILLBOARD_URL + music_prompt)
soup = BeautifulSoup(response.text, "html.parser")
song_time_period = soup.select("li ul li h3")
song_titles = [music.getText().strip() for music in song_time_period]

song_uris = []
year = music_prompt.split("-")[0]
for song in song_titles:
    result = sp.search(q=f"track: {song} year: {year}", type="track")
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")

playlist = sp.user_playlist_create(user=user_id, name=f"{year} Billboard Top 100", public=False)

sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)