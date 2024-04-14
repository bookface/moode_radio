#
# This is a modified copy of the Qt python example
# mediaplayer/player.py file.
# Volume not working except to mute
#

"""PySide6 Multimedia player example"""

import sys
from PySide6.QtCore import QStandardPaths, Qt, Slot, QSettings
from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtWidgets import (QApplication, QDialog, QFileDialog,
    QMainWindow, QSlider, QStyle, QToolBar)
from PySide6.QtMultimedia import (QAudioOutput, QMediaFormat,
                                  QMediaPlayer)
from PySide6.QtMultimediaWidgets import QVideoWidget

import os

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self._playlist = []
        self._playlist_index = -1
        self._audio_output = QAudioOutput()
        self._player = QMediaPlayer()
        self._player.setAudioOutput(self._audio_output)

        self._player.errorOccurred.connect(self._player_error)

        tool_bar = QToolBar()
        self.addToolBar(tool_bar)

        file_menu = self.menuBar().addMenu("&File")
        icon = QIcon.fromTheme("document-open")
        open_action = QAction(icon, "&Open...", self,
                              shortcut=QKeySequence.Open, triggered=self.open)
        file_menu.addAction(open_action)
        tool_bar.addAction(open_action)
        icon = QIcon.fromTheme("application-exit")
        exit_action = QAction(icon, "E&xit", self,
                              shortcut="Ctrl+Q", triggered=self.close)
        file_menu.addAction(exit_action)

        play_menu = self.menuBar().addMenu("&Play")
        style = self.style()
        icon = QIcon.fromTheme("media-playback-start.png",
                               style.standardIcon(QStyle.SP_MediaPlay))
        self._play_action = tool_bar.addAction(icon, "Play")
        self._play_action.triggered.connect(self._player.play)
        play_menu.addAction(self._play_action)

        icon = QIcon.fromTheme("media-skip-backward-symbolic.svg",
                               style.standardIcon(QStyle.SP_MediaSkipBackward))
        self._previous_action = tool_bar.addAction(icon, "Previous")
        self._previous_action.triggered.connect(self.previous_clicked)
        play_menu.addAction(self._previous_action)

        icon = QIcon.fromTheme("media-playback-pause.png",
                               style.standardIcon(QStyle.SP_MediaPause))
        self._pause_action = tool_bar.addAction(icon, "Pause")
        self._pause_action.triggered.connect(self._player.pause)
        play_menu.addAction(self._pause_action)

        icon = QIcon.fromTheme("media-skip-forward-symbolic.svg",
                               style.standardIcon(QStyle.SP_MediaSkipForward))
        self._next_action = tool_bar.addAction(icon, "Next")
        self._next_action.triggered.connect(self.next_clicked)
        play_menu.addAction(self._next_action)

        icon = QIcon.fromTheme("media-playback-stop.png",
                               style.standardIcon(QStyle.SP_MediaStop))
        self._stop_action = tool_bar.addAction(icon, "Stop")
        self._stop_action.triggered.connect(self._ensure_stopped)
        play_menu.addAction(self._stop_action)

        if False:
            self._volume_slider = QSlider()
            self._volume_slider.setOrientation(Qt.Horizontal)
            self._volume_slider.setMinimum(0)
            self._volume_slider.setMaximum(100)
            available_width = self.screen().availableGeometry().width()
            self._volume_slider.setFixedWidth(available_width / 10)
            self._volume_slider.setValue(self._audio_output.volume())
            self._volume_slider.setTickInterval(10)
            self._volume_slider.setTickPosition(QSlider.TicksBelow)
            self._volume_slider.setToolTip("Volume")
            self._volume_slider.valueChanged.connect(self._audio_output.setVolume)
            tool_bar.addWidget(self._volume_slider)

        self.update_buttons(self._player.playbackState())
        self._mime_types = []

        import getpass
        user = getpass.getuser()
        self.music_directory = f"/media/{user}/easystore/Music"

    def closeEvent(self, event):
        self._ensure_stopped()
        event.accept()

    def save(self,name):
        settings = QSettings('player.ini',QSettings.IniFormat)
        settings.setValue("last", name)

    def load(self):
        if os.path.isfile('player.ini'):
            settings = QSettings('player.ini',QSettings.IniFormat)
            name = settings.value('last')
            self.add(name)

    def open(self):
        self._ensure_stopped()
        file_dialog = QFileDialog(self,directory=self.music_directory)
        if file_dialog.exec() == QDialog.Accepted:
            url = file_dialog.selectedUrls()[0]
            self._playlist.append(url)
            self._playlist_index = len(self._playlist) - 1
            self._player.setSource(url)
            self._player.play()
            self.save(url)
            self.setWindowTitle(f"{url}")
            
    def add(self,filename):
        self._playlist.append(filename)
        self._playlist_index = len(self._playlist) - 1
        self._player.setSource(filename)
        self._player.play()
        self.setWindowTitle(f"{filename}")
        self.save(filename)
        
    def _ensure_stopped(self):
        if self._player.playbackState() != QMediaPlayer.StoppedState:
            self._player.stop()

    def previous_clicked(self):
        # Go to previous track if we are within the first 5 seconds of playback
        # Otherwise, seek to the beginning.
        if self._player.position() <= 5000 and self._playlist_index > 0:
            self._playlist_index -= 1
            self._playlist.previous()
            self._player.setSource(self._playlist[self._playlist_index])
        else:
            self._player.setPosition(0)

    def next_clicked(self):
        if self._playlist_index < len(self._playlist) - 1:
            self._playlist_index += 1
            self._player.setSource(self._playlist[self._playlist_index])

    @Slot("QMediaPlayer::PlaybackState")
    def update_buttons(self, state):
        media_count = len(self._playlist)

        if False:
            self._play_action.setEnabled(media_count > 0
                                         and state != QMediaPlayer.PlayingState)
            self._pause_action.setEnabled(state == QMediaPlayer.PlayingState)
            self._stop_action.setEnabled(state != QMediaPlayer.StoppedState)

        self._previous_action.setEnabled(self._player.position() > 0)
        self._next_action.setEnabled(media_count > 1)

    def show_status_message(self, message):
        self.statusBar().showMessage(message, 5000)

    @Slot("QMediaPlayer::Error", str)
    def _player_error(self, error, error_string):
        print(error_string, file=sys.stderr)
        self.show_status_message(error_string)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    available_geometry = main_win.screen().availableGeometry()

    if len(sys.argv) > 1:
        file = sys.argv[1]
        main_win.add(file)
    else:
        main_win.load()
        
    main_win.show()
    sys.exit(app.exec())
