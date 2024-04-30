# Discord Clip Uploader

This is a tool that lets you send your favorite videos through Discord (or Twitter) without having to worry about filesize limitations.
It works in 3 simple steps:
  - It uploads your videos to [FileDitch](https://fileditch.com/)
  - It uses [Discord AV1 Video Tool](https://autocompressor.net/av1?) to generate a link to the video
  - It copies it to your clipboard and voila, you can send it anywhere

This program works by exploiting a bug in Discord that forces it to display VERY large videos that wouldn't be embedded otherwise.

## How to use
- Go to [Releases](https://github.com/nekiak/discordclipuploader/releases/)
- Download the latest DiscordClipUploader.exe file and execute it
- If it doesn't open, try making an exception in your Antivirus


## If you want to run the code by yourself, these are the steps:
  1. `pip install -r requirements.txt`
  2. `python3 main.py`

This assumes that you already have Python 3+ installed.


## ⚠️ In case it flags your Antivirus software ⚠️

**It's just a false positive, this program is 100% opensource and does not contain any sort of malware or viruses**

The only way for me to make it not trigger your AV is to sign the program on Microsoft by paying $300 dollars, In case you're still worried, [**please read this comment**](https://github.com/Nuitka/Nuitka/issues/2495#issuecomment-1762836583)
