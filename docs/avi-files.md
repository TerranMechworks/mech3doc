# AVI files

The Mechwarrior 3 intro and campaign videos are found in the `video` directory on the CD. They can also optionally be installed to the hard drive.

## Investigation (MW3)

They are [AVI containers](https://en.wikipedia.org/wiki/Audio_Video_Interleave) (`*.avi`). The video codec is known from the installation, but we can confirm that and gather more information using   [`ffmpeg`](https://www.ffmpeg.org/), specifically `ffprobe`. This is for `campaign.avi`, information on all English video files can be found in the appendix:

```
Input #0, avi, from 'Campaign.avi':
  Duration: 00:03:24.27, start: 0.000000, bitrate: 3320 kb/s
  Stream #0:0: Video: indeo5 (IV50 / 0x30355649), yuv410p, 640x480, 3020 kb/s, 15 fps, 15 tbr, 15 tbn, 15 tbc
  Stream #0:1: Audio: pcm_u8 ([1][0][0][0] / 0x0001), 22050 Hz, 1 channels, u8, 176 kb/s
```

The video streams are encoded using Intel's [Indeo codec](https://en.wikipedia.org/wiki/Indeo) (version 5, FourCC `IV50`). They are all 640x480 at 15 frames per second, although the bitrates vary from 3020 kb/s to 1260 kb/s. The audio streams are raw [pulse-code modulation (PCM)](https://en.wikipedia.org/wiki/Pulse-code_modulation) at 22050 Hz, so uncompressed.

For the German version, these have the metadata "Sound Forge 4.0 Audio" attached, which was a [German sound editing program](https://en.wikipedia.org/wiki/Sound_Forge), probably used by the localisation team.

These codecs were no doubt chosen because they could be decoded with very little CPU, not because of their quality. This is especially true if they had to be streamed from the CD. Codecs have come far since then, with ubiquitous hardware support. Indeo has at least one [vulnerability](https://support.microsoft.com/en-us/help/954157/microsoft-security-advisory-vulnerabilities-in-the-indeo-codec-could-a), meaning the codec is unlikely to be installed on modern systems. Realistically, the best option is to re-encode at least the video using existing software (`ffmpeg`). Installing the old codec is obviously inadvisable, and reverse engineering the codec is complicated and unnecessary.

The file checksums between the US versions 1.0, 1.1, and 1.2 are exactly the same (on the CD - I don't think the patch affects the video files, simply based on the size, but haven't checked).

## Re-encoding

TL;DR:

```bash
for f in *.avi
do
    ffmpeg \
        -i "$f" \
        -codec:v "libx264" \
        -preset "medium" \
        -crf "30" \
        -codec:a "aac" \
        -b:a "64k" \
        "${f%.*}.mp4"
done
```

To compress the audio, there are several options. If supported, [advanced audio coding (ACC)](https://en.wikipedia.org/wiki/Advanced_Audio_Coding) is excellent at low bitrates, and for mainly speech, using 64 kb/s is fine without any concerns of quality loss. The command line options are `-codec:a aac -b:a 64k`[^libfdk]. AAC is patented and not all game engines support it. This is generally problematic for good audio codecs. A viable alternative is to not alter the audio and just copy it using `-codec:a copy`, as raw PCM support is ubiquitous.

As mentioned, I definitely wanted to re-encode the video because of known Indeo vulnerabilities. H.264/x264 is widely supported. Quality-wise, it's a bit trickier than the audio, because it's more subjective in comparisons. The original video is highly compressed, with visible compression artefacts - please keep this in mind, the re-encoded file can't be better than the original. So personally, I find the video re-encoded with a low bitrate fine. In fact, choosing a low bitrate smooths some of the original, block-y compression artefacts out (the smoothing could be done via processing at higher bitrates). But you can decide for yourself, in a minute I'll show how to compare the re-encoded to the original. And worst case, files can be re-encoded from the original again.

My recommendation is to use a fairly quick encoding to test things out, and a low quality factor. Something like `-codec:v libx264 -preset medium -crf 28`. It's worth reading the [`ffmpeg` H.264 encoding guide](https://trac.ffmpeg.org/wiki/Encode/H.264) if you wish to change these parameters. Choose a slower preset should deliver the same quality at a lower bitrate, at expense of encoding time. Choosing a lower `crf` value will increase the bitrate, which in theory increases quality. Given the source material, that probably won't do much those. Once you're happy with the parameters, I'd suggest using a slower preset for the final encoding, like `veryslow`, since processing power is cheap and these videos are short and have a tiny resolution (generally, the preset doesn't affect quality very much).

For a container format with maximum compatibility, I've chosen [MPEG-4](https://en.wikipedia.org/wiki/MPEG-4_Part_14) (`*.mp4`), although if supported by your use-case, the open standard [Matroska](https://matroska.org/) (`*.mkv`) is an excellent choice.

[^libfdk]: `libfdk` [might be slightly higher in quality](https://trac.ffmpeg.org/wiki/Encode/AAC), and if your build of `ffmpeg` was compiled with `libfdk` support you could try using the `libfdk_aac` codec. That also enabled the use of variable bit rate. However, I don't think it's worth the effort. The input isn't exactly high quality in the first place, and the built-in AAC encoder is pretty good.

### Comparing results

The [MPV](https://mpv.io/) media player [can play two (or more) videos side-by-side](https://superuser.com/a/1325668), which is great for comparing the encoded video. 

```bash
mpv --lavfi-complex="[vid1][vid2]hstack[vo]" intro.avi --external-file=intro.mp4
```

## In-game use

The introduction is played when the game is loading. The campaign videos are played when the campaign is started, and between missions.

## Appendix 1: Modern codec performance

It's interesting to see just how far codecs have come. For those settings, the average reduction in size is 86% for the US version and almost 89% for the German version!

**video/v1.0-us**

| Filename     | Original  | Compressed | Reduction |
|:-------------|----------:|-----------:|----------:|
| intro.avi    | 78.36 MiB |   5.47 MiB |     93.0% |
| Campaign.avi | 80.85 MiB |  12.45 MiB |     84.6% |
| c1.avi       | 14.50 MiB |   1.36 MiB |     90.6% |
| c1m1.avi     |  8.75 MiB |   0.97 MiB |     88.9% |
| c1m2.avi     |  5.96 MiB |   0.77 MiB |     87.0% |
| c1m3.avi     |  5.21 MiB |   0.74 MiB |     85.7% |
| c1m4.avi     |  9.17 MiB |   1.16 MiB |     87.4% |
| c2.avi       | 10.79 MiB |   1.67 MiB |     84.6% |
| c2m1.avi     |  4.77 MiB |   0.65 MiB |     86.4% |
| c2m2.avi     | 10.41 MiB |   1.22 MiB |     88.3% |
| c2m3.avi     |  6.31 MiB |   0.75 MiB |     88.2% |
| c2m4.avi     |  7.68 MiB |   0.79 MiB |     89.7% |
| c3.avi       |  5.48 MiB |   1.62 MiB |     70.5% |
| c3m1.avi     |  5.93 MiB |   1.06 MiB |     82.1% |
| c3m2.avi     |  6.24 MiB |   1.02 MiB |     83.6% |
| c3m4.avi     |  7.45 MiB |   1.12 MiB |     84.9% |
| c3m5.avi     |  9.49 MiB |   1.08 MiB |     88.6% |
| c3m6.avi     |  5.73 MiB |   0.84 MiB |     85.3% |
| c4win.avi    | 23.98 MiB |   1.49 MiB |     93.8% |

Average reduction: 86.5%

**video/v1.0-de**

| Filename     | Original  | Compressed | Reduction |
|:-------------|----------:|-----------:|----------:|
| intro.avi    | 76.00 MiB |   5.33 MiB |     93.0% |
| Campaign.avi | 77.76 MiB |  11.35 MiB |     85.4% |
| c1.avi       | 13.45 MiB |   1.36 MiB |     89.9% |
| c1m1.avi     | 10.88 MiB |   0.97 MiB |     91.1% |
| c1m2.avi     |  7.44 MiB |   0.77 MiB |     89.6% |
| c1m3.avi     |  6.50 MiB |   0.74 MiB |     88.5% |
| c1m4.avi     | 11.38 MiB |   1.16 MiB |     89.8% |
| c2.avi       | 13.32 MiB |   1.67 MiB |     87.5% |
| c2m1.avi     |  5.95 MiB |   0.65 MiB |     89.1% |
| c2m2.avi     | 12.86 MiB |   1.22 MiB |     90.5% |
| c2m3.avi     |  7.86 MiB |   0.75 MiB |     90.5% |
| c2m4.avi     |  9.46 MiB |   0.79 MiB |     91.6% |
| c3.avi       |  6.88 MiB |   1.62 MiB |     76.5% |
| c3m1.avi     |  7.38 MiB |   1.06 MiB |     85.6% |
| c3m2.avi     |  7.75 MiB |   1.02 MiB |     86.8% |
| c3m4.avi     |  9.27 MiB |   1.13 MiB |     87.9% |
| c3m5.avi     | 11.80 MiB |   1.08 MiB |     90.9% |
| c3m6.avi     |  7.15 MiB |   0.84 MiB |     88.3% |
| c4win.avi    | 23.98 MiB |   1.50 MiB |     93.8% |

Average reduction: 88.7%

## Appendix 2: English video file information 

```
Input #0, avi, from 'Campaign.avi':
  Duration: 00:03:24.27, start: 0.000000, bitrate: 3320 kb/s
  Stream #0:0: Video: indeo5 (IV50 / 0x30355649), yuv410p, 640x480, 3020 kb/s, 15 fps, 15 tbr, 15 tbn, 15 tbc
  Stream #0:1: Audio: pcm_u8 ([1][0][0][0] / 0x0001), 22050 Hz, 1 channels, u8, 176 kb/s
Input #0, avi, from 'c1.avi':
  Duration: 00:00:58.00, start: 0.000000, bitrate: 2096 kb/s
  Stream #0:0: Video: indeo5 (IV50 / 0x30355649), yuv410p, 640x480, 1236 kb/s, 15 fps, 15 tbr, 15 tbn, 15 tbc
  Stream #0:1: Audio: pcm_s16le ([1][0][0][0] / 0x0001), 22050 Hz, 2 channels, s16, 705 kb/s
Input #0, avi, from 'c1m1.avi':
  Duration: 00:00:46.00, start: 0.000000, bitrate: 1595 kb/s
  Stream #0:0: Video: indeo5 (IV50 / 0x30355649), yuv410p, 640x480, 1275 kb/s, 15 fps, 15 tbr, 15 tbn, 15 tbc
  Stream #0:1: Audio: pcm_u8 ([1][0][0][0] / 0x0001), 22050 Hz, 1 channels, u8, 176 kb/s
Input #0, avi, from 'c1m2.avi':
  Duration: 00:00:31.67, start: 0.000000, bitrate: 1577 kb/s
  Stream #0:0: Video: indeo5 (IV50 / 0x30355649), yuv410p, 640x480, 1263 kb/s, 15 fps, 15 tbr, 15 tbn, 15 tbc
  Stream #0:1: Audio: pcm_u8 ([1][0][0][0] / 0x0001), 22050 Hz, 1 channels, u8, 176 kb/s
Input #0, avi, from 'c1m3.avi':
  Duration: 00:00:27.73, start: 0.000000, bitrate: 1577 kb/s
  Stream #0:0: Video: indeo5 (IV50 / 0x30355649), yuv410p, 640x480, 1258 kb/s, 15 fps, 15 tbr, 15 tbn, 15 tbc
  Stream #0:1: Audio: pcm_u8 ([1][0][0][0] / 0x0001), 22050 Hz, 1 channels, u8, 176 kb/s
Input #0, avi, from 'c1m4.avi':
  Duration: 00:00:48.33, start: 0.000000, bitrate: 1591 kb/s
  Stream #0:0: Video: indeo5 (IV50 / 0x30355649), yuv410p, 640x480, 1268 kb/s, 15 fps, 15 tbr, 15 tbn, 15 tbc
  Stream #0:1: Audio: pcm_u8 ([1][0][0][0] / 0x0001), 22050 Hz, 1 channels, u8, 176 kb/s
Input #0, avi, from 'c2.avi':
  Duration: 00:00:56.67, start: 0.000000, bitrate: 1596 kb/s
  Stream #0:0: Video: indeo5 (IV50 / 0x30355649), yuv410p, 640x480, 1265 kb/s, 15 fps, 15 tbr, 15 tbn, 15 tbc
  Stream #0:1: Audio: pcm_u8 ([1][0][0][0] / 0x0001), 22050 Hz, 1 channels, u8, 176 kb/s
Input #0, avi, from 'c2m1.avi':
  Duration: 00:00:25.27, start: 0.000000, bitrate: 1584 kb/s
  Stream #0:0: Video: indeo5 (IV50 / 0x30355649), yuv410p, 640x480, 1270 kb/s, 15 fps, 15 tbr, 15 tbn, 15 tbc
  Stream #0:1: Audio: pcm_u8 ([1][0][0][0] / 0x0001), 22050 Hz, 1 channels, u8, 176 kb/s
Input #0, avi, from 'c2m2.avi':
  Duration: 00:00:54.40, start: 0.000000, bitrate: 1605 kb/s
  Stream #0:0: Video: indeo5 (IV50 / 0x30355649), yuv410p, 640x480, 1275 kb/s, 15 fps, 15 tbr, 15 tbn, 15 tbc
  Stream #0:1: Audio: pcm_u8 ([1][0][0][0] / 0x0001), 22050 Hz, 1 channels, u8, 176 kb/s
Input #0, avi, from 'c2m3.avi':
  Duration: 00:00:33.33, start: 0.000000, bitrate: 1587 kb/s
  Stream #0:0: Video: indeo5 (IV50 / 0x30355649), yuv410p, 640x480, 1270 kb/s, 15 fps, 15 tbr, 15 tbn, 15 tbc
  Stream #0:1: Audio: pcm_u8 ([1][0][0][0] / 0x0001), 22050 Hz, 1 channels, u8, 176 kb/s
Input #0, avi, from 'c2m4.avi':
  Duration: 00:00:39.80, start: 0.000000, bitrate: 1618 kb/s
  Stream #0:0: Video: indeo5 (IV50 / 0x30355649), yuv410p, 640x480, 1286 kb/s, 15 fps, 15 tbr, 15 tbn, 15 tbc
  Stream #0:1: Audio: pcm_u8 ([1][0][0][0] / 0x0001), 22050 Hz, 1 channels, u8, 176 kb/s
Input #0, avi, from 'c3.avi':
  Duration: 00:00:29.27, start: 0.000000, bitrate: 1570 kb/s
  Stream #0:0: Video: indeo5 (IV50 / 0x30355649), yuv410p, 640x480, 1264 kb/s, 15 fps, 15 tbr, 15 tbn, 15 tbc
  Stream #0:1: Audio: pcm_u8 ([1][0][0][0] / 0x0001), 22050 Hz, 1 channels, u8, 176 kb/s
Input #0, avi, from 'c3m1.avi':
  Duration: 00:00:31.47, start: 0.000000, bitrate: 1579 kb/s
  Stream #0:0: Video: indeo5 (IV50 / 0x30355649), yuv410p, 640x480, 1260 kb/s, 15 fps, 15 tbr, 15 tbn, 15 tbc
  Stream #0:1: Audio: pcm_u8 ([1][0][0][0] / 0x0001), 22050 Hz, 1 channels, u8, 176 kb/s
Input #0, avi, from 'c3m2.avi':
  Duration: 00:00:33.20, start: 0.000000, bitrate: 1575 kb/s
  Stream #0:0: Video: indeo5 (IV50 / 0x30355649), yuv410p, 640x480, 1252 kb/s, 15 fps, 15 tbr, 15 tbn, 15 tbc
  Stream #0:1: Audio: pcm_u8 ([1][0][0][0] / 0x0001), 22050 Hz, 1 channels, u8, 176 kb/s
Input #0, avi, from 'c3m4.avi':
  Duration: 00:00:39.53, start: 0.000000, bitrate: 1580 kb/s
  Stream #0:0: Video: indeo5 (IV50 / 0x30355649), yuv410p, 640x480, 1260 kb/s, 15 fps, 15 tbr, 15 tbn, 15 tbc
  Stream #0:1: Audio: pcm_u8 ([1][0][0][0] / 0x0001), 22050 Hz, 1 channels, u8, 176 kb/s
Input #0, avi, from 'c3m5.avi':
  Duration: 00:00:50.07, start: 0.000000, bitrate: 1590 kb/s
  Stream #0:0: Video: indeo5 (IV50 / 0x30355649), yuv410p, 640x480, 1270 kb/s, 15 fps, 15 tbr, 15 tbn, 15 tbc
  Stream #0:1: Audio: pcm_u8 ([1][0][0][0] / 0x0001), 22050 Hz, 1 channels, u8, 176 kb/s
Input #0, avi, from 'c3m6.avi':
  Duration: 00:00:30.40, start: 0.000000, bitrate: 1582 kb/s
  Stream #0:0: Video: indeo5 (IV50 / 0x30355649), yuv410p, 640x480, 1266 kb/s, 15 fps, 15 tbr, 15 tbn, 15 tbc
  Stream #0:1: Audio: pcm_u8 ([1][0][0][0] / 0x0001), 22050 Hz, 1 channels, u8, 176 kb/s
Input #0, avi, from 'c4win.avi':
  Duration: 00:01:12.20, start: 0.000000, bitrate: 2786 kb/s
  Stream #0:0: Video: indeo5 (IV50 / 0x30355649), yuv410p, 640x480, 2481 kb/s, 15 fps, 15 tbr, 15 tbn, 15 tbc
  Stream #0:1: Audio: pcm_u8 ([1][0][0][0] / 0x0001), 22050 Hz, 1 channels, u8, 176 kb/s
Input #0, avi, from 'intro.avi':
  Duration: 00:03:02.47, start: 0.000000, bitrate: 3602 kb/s
  Stream #0:0: Video: indeo5 (IV50 / 0x30355649), yuv410p, 640x480, 2764 kb/s, 15 fps, 15 tbr, 15 tbn, 15 tbc
  Stream #0:1: Audio: pcm_s16le ([1][0][0][0] / 0x0001), 22050 Hz, 2 channels, s16, 705 kb/s
```
