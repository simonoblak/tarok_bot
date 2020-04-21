import winsound


class MusicPlayer:
    @staticmethod
    def play_sound(song_title):
        winsound.PlaySound(song_title, winsound.SND_ASYNC | winsound.SND_ALIAS)

    @staticmethod
    def stop_sound():
        winsound.PlaySound(None, winsound.SND_PURGE)
