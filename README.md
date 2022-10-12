<h1 align="center">
  <br>
  I Swear I'll Stop
  <br>
</h1>

<h4 align="center">My girlfriend wants me to stop swearing. Let's ask <a href="https://github.com/openai/whisper" target="_blank">Whisper</a> for some help.</h4>
<h5 align="center">Automatically detect swear words and alert using an audible sound and a DBus notification</h5>

<p align="center">
  <a href="#key-features">Key Features</a> •
  <a href="#how-to-use">How To Use</a> •
  <a href="#credits">Credits</a> •
  <a href="#license">License</a>
</p>

## Key Features

* Real-time audio processing from raw microphone input
* OpenAI Whisper inference
* GPU & CPU support
* Audio alarm and DBus system notifications

## How To Use

To clone and run this application, you'll need [Git](https://git-scm.com) and [Python](https://www.python.org/) installed on your computer. From your command line:

```bash
# Clone this repo.
git clone https://github.com/sam-ulrich1/i-swear-ill-stop
cd i-swear-ill-stop

# Install this repo's dependencies.
sudo apt install build-essential libdbus-glib-1-dev libgirepository1.0-dev ffmpeg portaudio19-dev
pip install -r requirements.txt

# Run the app!
python main.py
```

## Credits

This software uses the following open source packages:

- [OpenAI Whisper](https://github.com/openai/whisper)
- [whisper_mic](https://github.com/mallorbc/whisper_mic)
- [SpeechRecognition](https://github.com/Uberi/speech_recognition)
- [PyAudio](https://people.csail.mit.edu/hubert/pyaudio)
- [Bad Words File](https://github.com/LDNOOBW/List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words/blob/master/en)
- <a href="https://www.flaticon.com/free-icons/swear" title="swear icons">Swear icons created by Smashicons - Flaticon</a>

## License

MIT

