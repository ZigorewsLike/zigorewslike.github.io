---
title: "AudioNetLab"
category: python
summary: "A desktop music player for Windows where a neural network labels the genre as the track plays and a 20-band equalizer follows it. A custom audio path on top of PortAudio, a SQLite library, and inference run locally through ONNX Runtime."
date: 2026-07
featured: true
tags: [audio, ml, onnx, desktop]
tech: [Python, PyQt6, PortAudio, NumPy, SciPy, librosa, ONNX Runtime, SQLAlchemy, SQLite, OpenGL, PyInstaller]
cover: hero.png
#banner: banner.png
links:
  - { label: "GitHub", url: "https://github.com/ZigorewsLike/AudioNetLab", icon: github }
---

## What it is

AudioNetLab is a desktop music player for Windows: an album library, a play queue, an equalizer,
and tag and lyrics panels. What sets it apart from an ordinary player is that the genre of the
playing track is determined by a neural classifier, and the 20-band equalizer adapts to the labelled
genre as playback goes on.

Equalizer presets in players are switched by hand and for a whole track at a time, so on a
compilation, or on a track whose character changes, the setting stays a compromise. Here the
labelling is done per three-second fragment, and the target preset changes together with the
fragment.

All processing is local: the model is stored in the repository and runs on the CPU through ONNX
Runtime, and in the default configuration the application makes no network requests.

<figure>
  <img src="/projects/audionetlab/assets/hero.png" alt="AudioNetLab main window" loading="lazy">
  <figcaption>The main window: an album card with its tracklist, and the player with a waveform at the bottom</figcaption>
</figure>

## What it is made of

Four subsystems that meet at the equalizer.

### Audio path

Playback is implemented from scratch on top of PortAudio, without QtMultimedia. The track is decoded
into memory, and from there a producer and consumer scheme takes over: a background thread cuts the
waveform into blocks, passes them through the equalizer and writes the result into a ring buffer,
while the PortAudio callback, on its own high priority thread, only copies the ready float32 frames
to the device. The callback does no processing and no memory allocation, so load on the interpreter
and the interface does not turn into dropouts.

Consequences of the scheme:

- The output device and the device buffer size (512..16384 frames) can be changed during playback.
  The device buffer sets the tolerance to dropouts, while the producer's processing block is
  independent and stays short, so the response time of the equalizer does not depend on the buffer
  size.
- The volume is applied in the callback, past the buffer, so a change of the slider is heard
  immediately rather than after the already processed backlog has played out.
- Every seek increments a generation counter. A block computed before the seek and finished after it
  is discarded instead of sounding as a fragment of the previous position.

### Genre classifier

The track is split into 3-second fragments. Each fragment is reduced to a vector of 57 features
(chroma, RMS, spectral centroid, bandwidth and rolloff, zero-crossing rate, harmonic and percussive
statistics, tempo, and the mean and variance of 20 MFCC coefficients), standardised with the same
scaler as in training, and classified into one of eight FMA genres.

Two problems were solved separately:

- **Stability of the label.** A fragment whose top probability is below 0.85 inherits the label of
  the previous one: otherwise the transitions produce single-fragment outliers that are not in the
  music itself.
- **Cost of a repeated run.** The bulk of the time goes into extracting the librosa features rather
  than into inference, so the vectors are cached in the track registry and a repeated
  classification comes down to running the model.

The result is a label per 3 seconds across the whole track, presented as a coloured timeline, along
with the genre shares and the final genre. Classification runs on a separate thread and the
interface stays usable while it works.

<figure>
  <img src="/projects/audionetlab/assets/eq-ai.png" alt="EQ AI tab: genre timeline and equalizer" loading="lazy">
  <figcaption>The EQ AI tab: the genre timeline over the track, the genre shares and the live 20-band EQ</figcaption>
</figure>

### Equalizer and Auto EQ

The 20-band equalizer works in the frequency domain: an STFT is computed for every block, the
spectrum is multiplied by a gain mask assembled from the bands, and transformed back. This is
cheaper than a bank of IIR filters and allows the settings to change on the fly: new gains take
effect within one block, without restarting the stream.

The lookahead held in the buffer would keep an edit inaudible until the already computed audio runs
out, so while the equalizer is being used the producer shortens the lookahead to about 120 ms and
recomputes the tail of the buffer. Once the interaction ends, the lookahead returns to a second and
the path is protected against scheduler delays again.

In Auto EQ mode the player takes the genre under the playback cursor, reads the preset saved for
that genre, and on every position update moves each band towards it by a fraction of the remaining
distance. At the boundary of two genres the curve crosses over across several updates instead of in
one, so a change of preset produces no audible click.

<figure>
  <img src="/projects/audionetlab/assets/auto-eq.gif" alt="Auto EQ interpolation" loading="lazy">
  <figcaption>Auto EQ interpolation at a genre boundary</figcaption>
</figure>

### Library

The library is SQLite through SQLAlchemy: tracks, artists, albums, covers and scanned folders. Files
are not copied, the database keeps the path, the tags and the statistics. Folder scanning is moved
to a separate thread, progress and cancellation are shown on a strip above the player, the window
stays usable while a scan runs, and a cancelled pass keeps everything it managed to import.

The schema is versioned through `PRAGMA user_version`, and the migrations are functions in a list of
steps, each in its own transaction, with no Alembic. The database is opened in WAL mode with
`busy_timeout`, because the scanner writes from its own thread in parallel with the player.

<figure>
  <img src="/projects/audionetlab/assets/library-albums.png" alt="Library tab, album grid" loading="lazy">
  <figcaption>The Library tab, Albums view</figcaption>
</figure>

### Interface

PyQt6, a frameless window with a custom title bar, an OpenGL waveform with zoom and panning, tag,
lyrics and queue panels, and Russian and English localisation through Qt Linguist with language
switching that needs no restart. The executable is built with PyInstaller.

## Engineering notes

The main bottlenecks and how they are closed.

**Importing a large collection.** The limit was not the database but reading tags and covers. A file
whose modification time has not changed is never opened again, so a rescan of a collection of 3663
tracks costs 0.1 s. FLAC tags are read by a custom parser that skips past the artwork block instead
of loading it in full: 0.6 KB per track instead of 306 KB.

**Covers.** They are decoded once per album rather than per track, and stored in the cache already
scaled down, under the name of the hash of the source image. Albums with the same artwork use one
file, and painting the grid comes down to reading a few kilobytes of JPEG instead of a full decode.

**Album grid.** Implemented as a `QListView` with a `QStyledItemDelegate` rather than a widget per
album, so only the visible tiles are painted and the cost per repaint does not grow with the size of
the library. Covers are loaded outside the interface thread: a tile shows a placeholder, and when
the image is ready only that tile is repainted.

**Deduplication of artists and albums.** The matching keys are casefolded in Python instead of
`COLLATE NOCASE`: SQLite only folds ASCII and would file "Ария" and "ария" as two different artists.
An album is assembled by the `ALBUMARTIST` tag, otherwise a compilation falls apart into
single-track albums.

**Missing files.** A track that is not on disk is flagged rather than deleted, so an unplugged
external drive does not take the library and the play counts with it. The flag is cleared by the
next scan that finds the file in place.

## Size and stack

About 15 000 lines of Python in 118 modules under `src/`. Python 3.10, PyQt6, PortAudio through
PyAudio, NumPy and SciPy, librosa, ONNX Runtime, SQLAlchemy and SQLite, OpenGL for drawing the
waveform, PyInstaller for the build. The modules that need an external HTTP service (transcription,
translation and summarization of lyrics) sit behind a flag and are off by default, so an ordinary
build runs fully offline.
