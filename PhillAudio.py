import simpleaudio as sa


def play_wav_file(sub_folder: str, file_name: str):
    wave_obj = sa.WaveObject.from_wave_file("cache/" + sub_folder + "/" + file_name)
    wave_obj.play()
