""" tkVideo: Python module for playing videos (without sound) inside tkinter Label widget using Pillow and imageio
This library is a modification on the tkVideo library provided by Xenofon Konitsas (Copyright © 2020 Xenofon Konitsas <konitsasx@gmail.com>)
Originally Released under the terms of the MIT license (https://opensource.org/licenses/MIT) as described in LICENSE.md

To make the library work under required condition, a new class had to be made to call the playertask class into.
The original library could start a video, but not stop it. The new class has been made to start and stop a tread that plays the video.
This makes the class capable to restart a new video instead.
"""

import threading
import imageio
from PIL import Image, ImageTk


class PlayerTask:
    """
    This class is the thread that plays the video.
    """
    def __init__(self, size):
        self._running = True
        self.size = size

    def terminate(self):
        self._running = False

    def run(self, path, label, loop):
        """
            Loads the video's frames recursively onto the selected label widget's image parameter.
            Loop parameter controls whether the function will run in an infinite loop
            or once.
        """
        frame_data = imageio.get_reader(path)

        if loop == 1:
            while self._running:
                for image in frame_data.iter_data():
                    frame_image = ImageTk.PhotoImage(Image.fromarray(image).resize(self.size))
                    label.config(image=frame_image)
                    label.image = frame_image
                    if not self._running:
                        break

        else:
            for image in frame_data.iter_data():
                frame_image = ImageTk.PhotoImage(Image.fromarray(image).resize(self.size))
                label.config(image=frame_image)
                label.image = frame_image


class tkvideo():
    """
        This class maintains the thread that plays a video
    """

    def __init__(self, label, loop=0, size=(640, 360)):
        self.label = label
        self.loop = loop
        self.size = size
        self.thread = None
        self.player = None

    def play(self, video_path):
        """
            Creates and starts a thread as a daemon that plays the video by rapidly going through
            the video's frames.
        """

        if self.player:
            self.stop()

        self.player = PlayerTask(self.size)

        self.thread = threading.Thread(target=self.player.run, args=(video_path, self.label, self.loop))
        # self.thread = threading.Thread(target=self.load, args=(video_path, self.label, self.loop))
        self.thread.daemon = 1
        self.thread.start()

    def stop(self):
        self.player.terminate()
        print("terminate")



