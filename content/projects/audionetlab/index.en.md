---
title: "AudioNetLab"
category: python
summary: "A desktop music player for Windows with a neural genre classifier in the playback path: the track is split into 3-second fragments, and a 20-band equalizer follows the genre under the cursor."
date: 2026-07
featured: true
tags: [audio, ml, onnx, desktop]
tech: [Python, PyQt6, ONNX Runtime, librosa, SQLAlchemy, SQLite, OpenGL]
cover: hero.png
links:
  - { label: "GitHub", url: "https://github.com/ZigorewsLike/AudioNetLab", icon: github }
---

## About

AudioNetLab is a desktop music player for Windows built around a genre classifier that runs on the
track being played. The track is split into 3-second fragments; each one is reduced to a 57-value
feature vector (chroma, RMS, spectral centroid, bandwidth and rolloff, zero-crossing rate, harmonic
and percussive statistics, tempo, and the mean and variance of 20 MFCC coefficients), standardised
with the scaler from the training pipeline, and classified into one of eight FMA genres. A fragment
whose top probability is below 0.85 keeps the label of the previous one, which suppresses
single-fragment flicker at transitions.

<figure>
  <img src="/projects/audionetlab/assets/hero.png" alt="AudioNetLab main window" loading="lazy">
  <figcaption>The main window: an album card with its tracklist, and the player with a waveform at the bottom</figcaption>
</figure>

The output is a genre label per fragment across the whole track, drawn as a timeline. The player
uses it to drive the equalizer: in Auto EQ mode the 20 band gains follow the genre under the
playback cursor and interpolate towards the preset saved for that genre instead of switching in one
step. Equalisation is applied to every playback chunk as a gain mask over the STFT, so a change in
the gains takes effect within one chunk without interrupting the stream.

<figure>
  <img src="/projects/audionetlab/assets/eq-ai.png" alt="EQ AI tab: genre timeline and equalizer" loading="lazy">
  <figcaption>The EQ AI tab: the genre timeline over the track, genre shares and the live 20-band EQ</figcaption>
</figure>

The rest is a conventional player: a SQLite library with a folder scanner and an album grid, a play
queue, an OpenGL waveform view, tag and lyrics panels, and an English/Russian interface.

Inference is local: the model is part of the repository and runs through ONNX Runtime on the CPU,
and in the default configuration the application makes no network requests.

## What's inside

- **Playback.** MP3, FLAC and WAV, decoded into memory and streamed to the output device from a
  background thread. The device and the PortAudio buffer size (512..16384 frames) can be changed
  while a track is playing.
- **Genre classification.** A label per 3 seconds, a coloured timeline, the share of each genre and
  the final one. Feature vectors are cached per track, so a repeated run is inference only.
- **20-band equalizer.** Applied in the frequency domain to every chunk; gains are stored as a
  preset per genre.
- **Auto EQ.** Bands move towards the current genre's preset by a fraction of the remaining
  distance per update, with an adjustable divisor from 2 to 20.
- **Library.** SQLite, a folder scanner on its own thread, an album grid and a flat track list with
  search and sort, a play queue, and a cover cache deduplicated by image hash.

## How it works

Playback and classification are two separate paths that meet at the equalizer. The track is decoded
into memory and pushed to the output device chunk by chunk on a background thread, and every chunk
passes through the STFT equalizer on its way out:

```txt
decode → buffer → streaming thread → per-chunk STFT equalizer → output device
```

Auto EQ looks up the genre under the playback cursor, takes that genre's saved preset and moves each
band towards it by a fraction of the remaining distance on every position update. Where two genres
meet, the EQ curve crosses over across several updates instead of in one.

<figure>
  <img src="/projects/audionetlab/assets/auto-eq.gif" alt="Auto EQ interpolation" loading="lazy">
  <figcaption>Auto EQ interpolation at a genre boundary</figcaption>
</figure>

The first prediction of a track is the slow one, because the librosa features have to be extracted.
They are cached in the track registry, so predicting the same track again only re-runs the model.

## Engineering notes

Importing a large collection was bound by tags and covers, so a file whose modification time did
not change is never opened again (a rescan of 3663 tracks costs 0.1 s), and FLAC tags are read by a
small parser that seeks past the artwork block instead of loading it: 0.6 KB per track instead of
306 KB. The cover is decoded once per album and cached under the hash of the image, so albums
sharing artwork share one file.

<figure>
  <img src="/projects/audionetlab/assets/library-albums.png" alt="Library tab, album grid" loading="lazy">
  <figcaption>The Library tab, Albums view</figcaption>
</figure>

The album grid is a `QListView` with a `QStyledItemDelegate` rather than a widget per album, so only
the visible tiles are painted and the cost per repaint does not grow with the size of the library.
The database schema is versioned through `PRAGMA user_version`: migrations are functions in a list
of steps, each in its own transaction, with no Alembic. Artists and albums are deduplicated on a key
casefolded in Python instead of `COLLATE NOCASE`, because SQLite only folds ASCII and would file
"Ария" and "ария" as two different artists.