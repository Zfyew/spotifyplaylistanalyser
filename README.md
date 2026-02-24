# Spotify Playlist Analyser

Python tool that connects to your Spotify account and runs a full analysis 
on any playlist. Pulls track data, audio features, genre breakdown, mood 
patterns and top artists, then prints a summary report in the terminal.

## Requirements

Spotify Premium is required to access audio features via the Web API.

You will also need a Spotify Developer account and app set up at 
developer.spotify.com. Add your Client ID, Client Secret and redirect URI 
to the top of the script before running.

## How to run

    pip install spotipy
    python spotifyanalyser.py

A browser window will open to authorise the app. After that pick a 
playlist number from the list and the report will print automatically.

## What it analyses

- Genre breakdown across all artists in the playlist
- Average energy, mood, danceability, tempo and acousticness
- Overall vibe label based on energy and mood scores
- Top 10 artists by track count
