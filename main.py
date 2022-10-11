import io
import queue
import re
import threading
import time
import vlc
import dbus

from pydub import AudioSegment
import speech_recognition as sr
import whisper
import tempfile
import os
import click

@click.command()
@click.option("--model", default="tiny", help="Model to use",
              type=click.Choice(["tiny", "base", "small", "medium", "large"]))
@click.option("--english", default=False, help="Whether to use English model", is_flag=True, type=bool)
@click.option("--verbose", default=False, help="Whether to print verbose output", is_flag=True, type=bool)
@click.option("--device", default=None, help="GPU device to run the Whisper model on", type=int)
@click.option("--bad-words-path", default="bad_words.txt", help="Path to badwords file", type=str)
@click.option("--alarm", default="alarm.mp3", help="Alarm sound path", type=str)
@click.option("--sample-rate", default=64_000, help="Sample rate of audio", type=int)
@click.option("--read-seconds", default=.5, help="Amount of seconds to read from the mic before queuing", type=float)
@click.option("--time-buffer", default=3, help="Size of the input buffer in seconds", type=float)
@click.option("--alert-icon", default="swear.png", help="Path to icon for swear bot notifications", type=str)
def main(model, english, verbose, device, bad_words_path, alarm, sample_rate, read_seconds,
         time_buffer, alert_icon):
    alert_icon = os.path.abspath(alert_icon)
    alarm = os.path.abspath(alarm)

    if model != "large" and english:
        model = model + ".en"
    audio_model = whisper.load_model(model, device=f"cuda:{device}" if device is not None else "cpu")

    # load bad words
    with open(bad_words_path) as f:
        BAD_WORDS = [x for x in f.read().split("\n") if len(x) > 0]

    q = queue.Queue(maxsize=-1)

    with sr.Microphone(sample_rate=sample_rate) as source:
        def process_sample():
            buffer = []
            timestamps = []

            bad_word_alerts = []

            while True:
                audio_data, timestamp = q.get(block=True, timeout=None)

                if verbose:
                    print("Queue Size: ", q.qsize())

                buffer.append(audio_data)
                timestamps.append(timestamp)
                if (len(buffer) * read_seconds) > time_buffer:
                    buffer.pop(0)
                    timestamps.pop(0)

                raw_audio_data = b''.join(buffer)
                data = io.BytesIO(sr.AudioData(raw_audio_data, source.SAMPLE_RATE, source.SAMPLE_WIDTH).get_wav_data())
                audio_clip = AudioSegment.from_file(data)

                temp_audio_path = tempfile.mktemp(suffix=".wav")

                audio_clip.export(temp_audio_path, format="wav")

                if english:
                    result = audio_model.transcribe(temp_audio_path, language='english')
                else:
                    result = audio_model.transcribe(temp_audio_path)

                try:
                    os.remove(temp_audio_path)
                except:
                    pass

                if verbose:
                    print("Raw Result: ", result)

                predicted_text = result["text"]

                if len(predicted_text) == 0:
                    continue

                cleaned_text = re.sub(r'[^\w\s]', '', predicted_text.lower())

                words = cleaned_text.split()

                if verbose:
                    print("Words; ", words)

                if len(words) == 0:
                    continue

                bad_words = []
                for word_idx, word in enumerate(words):
                    for bw in BAD_WORDS:
                        if word == bw:
                            bad_words.append((word_idx, word))
                            break

                if verbose:
                    print("Bad Words: ", bad_words)

                if len(bad_words) == 0:
                    continue

                bad_words = [x[1] for x in bad_words]
                bad_word_alerts = [ts for ts in bad_word_alerts if ts >= timestamps[0]]

                alerted = False
                for ts in timestamps:
                    if ts in bad_word_alerts:
                        if verbose:
                            print("Skipping for existing alert")
                        alerted = True
                        break

                if alerted:
                    continue

                if len(bad_words) == 0:
                    continue

                bad_word_alerts = timestamps

                if alarm == "none":
                    os.system("beep -f 555 -l 460")
                else:
                    # load alarm
                    alarm_player = vlc.MediaPlayer(alarm)
                    alarm_player.play()
                    time.sleep(.2)
                    while alarm_player.is_playing():
                        time.sleep(.1)
                    alarm_player.release()

                notify = dbus.Interface(
                    dbus.SessionBus().get_object("org.freedesktop.Notifications", "/org/freedesktop/Notifications"),
                    "org.freedesktop.Notifications"
                )
                notify.Notify("Swear Bot", 42069, alert_icon, "Swear Alert",
                              f"You said {'a bad word' if len(bad_words) == 1 else 'some bad words'}: {', '.join(bad_words)}",
                              [], [], 10000
                )

        threading.Thread(target=process_sample, daemon=True).start()

        while True:
            data = source.stream.read(int(sample_rate * read_seconds))

            q.put((data, time.time()))


main()