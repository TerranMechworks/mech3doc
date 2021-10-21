# Sound archives

Sound archives hold sound effects, used throughout the game in menus and in missions.

## Investigation

Sound archives are the easiest type of archive to investigate in my opinion. Their contents makes it obvious how [archive files](archive-files.md) are read.

The two hints as to what data these archives contain are that a) the 1.2 patch installs loose [Waveform Audio Files](https://en.wikipedia.org/wiki/WAV), aka. WAVE or `.wav` into the `zbd` directory, and b) the starting data in the archives is `b"RIFF \xe0\x02\x00WAVEfmt "`, which is the magic `RIFF` header ([Resource Interchange File Format](https://en.wikipedia.org/wiki/Resource_Interchange_File_Format)), and a `WAVE` format.

There isn't much else to say about these files, since the hard part is reading the archive, and that code is common with other archives.

Maybe of interest for parsing the WAVE files to read the raw sound data as floating point values is that they are all mono or stereo files, and use only 8 or 16 bit samples. RIFF or WAVE parsing is out of scope for this documentation, but I have had no problems with parsing the sound files.

Another thing to remember is that as mentioned, the patch installs loose WAVE files in the `zbd` directory, which also need to be loaded to have all sound effects present.

## In-game use

Sound effects are used throughout the game in menus and in missions. They are global, so it's easy to load them once and use them as needed throughout. With modern RAM sizes, this isn't a problem. The high fidelity sound archive is less than 100 MiB, and WAVE files are already uncompressed. Even if the sound data is parsed to floating point values, this should be less than 400 MiB.
