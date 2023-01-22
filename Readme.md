
SWAT 3 CMP to WAV audio decompression tool 
==========================================

Features
--------
This tool is capable of extracting SWAT 3 CMP sound files to common WAV format.
SWAT 3 used a proprietary, lossy format for these sound files and using them with
other software is not possible without first extracting them with this tool.
The file format and how it was reversed is further explained in
[a blog post](https://induktio.github.io/2016/08/26/audio-file-format-unpacking/).
This tool requires standard installation of Python 3. No optional packages needed.

CMP sound files contain all of the dialogue and music included in the game, usually encoded
in 22 kHz sampling rate which limits the quality. This tool does not attempt to upscale
the sound files using more sophisticated algorithms, although it could be possible in theory.
Due to the cumulative errors present in the lossy format, this tool only applies a minor filtering
to cancel out the noise effect which would otherwise cause issues in decoding longer audio files.


Usage
-----
```
./cmpreader.py [-v] [-t] input_filename.cmp
```
Decoded audio files are written to `output` directory using the same filename prefix.


Changelog
---------
### 2023-01-22
* Updated older published version to use Python 3.


License
-------
Redistribution and use in source and binary forms, with or without modification,
are permitted provided that you link to [the source repository](https://github.com/induktio/swat3-tools) 
or mention the original author in a similar way.

