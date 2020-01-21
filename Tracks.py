# -*- coding: utf-8 -*-
"""
Created on Sat Nov  2 20:03:30 2019

@author: Julian Cuero
"""

import xml.etree.ElementTree as ET
import sqlite3
conn = sqlite3.connect('Tracksdbs.sqlite')
# database handle cursor
cur = conn.cursor()
# Making some fresh tables using executescript()
cur.execute('DROP TABLE IF EXISTS Track;')
cur.execute('DROP TABLE IF EXISTS Album;')
cur.execute('DROP TABLE IF EXISTS Artist;')
cur.execute('DROP TABLE IF EXISTS Genre;')

cur.execute(''' 
CREATE TABLE Track (
id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
title TEXT UNIQUE,
len INTEGER,
rating INTEGER,
album_id INTEGER,
count INTEGER,
genre_id INTEGER
);
''')

cur.execute('''CREATE TABLE Album (
id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
title TEXT UNIQUE,
artist_id INTEGER
);
''')

cur.execute('''CREATE TABLE Artist (
id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
name TEXT UNIQUE
);
''')

cur.execute(''' 
CREATE TABLE Genre (
id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
name TEXT UNIQUE
);
''')
def lookup (d, key):
    found = False
    for child in d:
        if found:
            return child.text
        if child.tag == 'key' and child.text == key:
            found = True
    return None
file = ET.parse('Library.xml')
stuff = file.findall('dict/dict/dict')
print('Dict count:', len(stuff))
for entry in stuff:
    if lookup(entry, 'Track ID') is None:
        continue
    name = lookup(entry, 'Name')
    artist = lookup(entry, 'Artist')
    album = lookup(entry, 'Album')
    length = lookup(entry, 'Total Time')
    rating = lookup(entry, 'Rating')
    count = lookup(entry, 'Play Count')
    genre = lookup(entry, 'Genre')
    if name is None or artist is None or album is None or length is None:
        continue
    print(name, artist, album, length, rating, count, genre)
    # Insert or ignore if it is already there
    cur.execute('''INSERT OR IGNORE INTO Artist(name) VALUES (?)
    ''', (artist,))
    cur.execute('SELECT id FROM Artist WHERE name = ?', (artist,))
    artist_id = cur.fetchone()[0]

    cur.execute('''INSERT OR IGNORE INTO Album (title, artist_id) VALUES (?, ?)
    ''', (album, artist_id))
    cur.execute('''SELECT id FROM Album WHERE title = ?''', (album,))
    album_id = cur.fetchone()[0]
    
    cur.execute(''' INSERT OR IGNORE INTO Genre(name) VALUES (?)
                ''', (genre,))
    cur.execute('SELECT id FROM Genre WHERE name = ?', (genre,))
    genre_id = cur.fetchone()[0]
    
    cur.execute('''INSERT OR REPLACE INTO Track 
            (title, len, rating, album_id, count, genre_id) 
            VALUES (?, ?, ?, ?, ?, ?)''', (name, length, rating, album_id, count, genre_id))

    conn.commit()
#Track artist album genre 3 rows
sqlstr = '''SELECT Track.title, Artist.name, Album.title, Genre.name
            FROM Track JOIN Genre JOIN Album JOIN Artist ON Track.genre_id = Genre.id AND
            Track.album_id = Album.id AND Album.artist_id = Artist.id 
            ORDER BY Artist.name LIMIT 3'''
cur.execute(sqlstr)
###################################
