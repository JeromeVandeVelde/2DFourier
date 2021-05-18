from tkinter import filedialog
from tkinter import *
from PIL import ImageTk
from PIL import Image
import PIL.Image

import BorderDetection
import pixelExtraction
import FFT

# define global variables
im = None
pixelarray = None


def placeImage(canvas, img, CanvasWidth, CanvasHeight):
    """
    this function places an image inside a specified canvas of the GUI.
    :param canvas: Defines the canvas to place the image in.
    :param img: Defines the image to place in the canvas.
    :param CanvasWidth: Defines the width of the canvas.
    :param CanvasHeight: Defines the height of the canvas.
    :return: None
    """
    img = img.resize((CanvasWidth, CanvasHeight))
    render = ImageTk.PhotoImage(img)
    img = Label(image=render)
    img.image = render
    canvas.create_image(0, 0, anchor=NW, image=render)


def upload(canvas, label, CanvasWidth, CanvasHeight):
    """
    This function allows the user to upload a file into the GUI.
    :param canvas: Defines the canvas to place the selected image in.
    :param label: Defines the label to place the filename in.
    :param CanvasWidth: Defines the width of the canvas.
    :param CanvasHeight: Defines the height of the canvas.
    :return: None
    """
    filename = filedialog.askopenfilename()
    try:
        img = Image.open(filename)
        placeImage(canvas, img, CanvasWidth, CanvasHeight)
        label.configure(text=filename)
        # do stuff
    except IOError:
        print("is not image")
        # filename not an image file
    return


def executeDB(filename, canvas, kernel, edgeThinning, CanvasWidth, CanvasHeight, verbose=0):
    """
    This functions generates border detection of a specific file, and places the return into a canvas.
    the border detection an be assisted with specific parameters.
    :param filename: Defines the file to run border detection over.
    :param canvas: Defines the canvas to show the result in.
    :param kernel: Defines the kernel used for border detection.
    :param edgeThinning: Defines if edge thinning should be applied.
    :param CanvasWidth: Defines the width of the canvas.
    :param CanvasHeight: Defines the height of the canvas.
    :param verbose: Defines level of commentary in the console.
    :return: The resulting image.
    """
    global im

    # reading the image
    im = PIL.Image.open(filename)
    original_width, original_height = im.size

    if verbose > 1:
        print("original width:", original_width)
        print("original height:", original_height)
        if edgeThinning:
            print("edgeThinning is on")
        else:
            print("edgeThinning is off")

    # grayscale the image
    if verbose > 0:
        print("grayscaling the picture")
    im = im.convert('L')

    # border detection:
    if verbose > 0:
        print("border detection")
    if edgeThinning:
        im = BorderDetection.blur(im)
    im = BorderDetection.border(im, kernel)
    im.save("FFT_1_border.png")
    placeImage(canvas, im, CanvasWidth, CanvasHeight)


def executeCB(canvas, RadiusLimit, minimumPoints, requestedpoints, new_width, CanvasWidth, CanvasHeight, verbose=0):
    """
    This function returns an array of pixels defining the contour of a specified border of an image.
    :param canvas: Defines the file to run border detection over.
    :param RadiusLimit: Defines the limit of the search radius in pixels.
    :param minimumPoints: Defines the minimum amount of points the crawler should return.
    :param requestedpoints: defines the amount of points the resulting array should return.
    :param new_width: Defines the new width of the generated image.
    :param CanvasWidth: Defines the width of the canvas.
    :param CanvasHeight: Defines the height of the canvas.
    :param verbose: Defines level of commentary in the console.
    :return: the resulting pixel array.
    """
    global im
    global pixelarray
    pixelarray = []

    original_width, original_height = im.size

    # extract pixels list
    if verbose > 0:
        print("pixel extraction")

    pixelarray = pixelExtraction.pixels(im, RadiusLimit, minimumPoints, verbose=(verbose - 1))

    # rescale pixels array size
    if verbose > 0:
        print("pixel array rescaling")
        print("requested points = ", requestedpoints)
    pixelarray = pixelExtraction.rescale_array(pixelarray, requestedpoints, verbose=(verbose - 1))

    # picture rescaling
    if verbose > 0:
        print("picture rescaling")
    scalefactor = new_width / original_width
    new_height = original_height * scalefactor
    pixelarray = pixelExtraction.rescale_picture(pixelarray, scalefactor, verbose=(verbose - 1))

    # draw resulting picture
    if verbose > 0:
        print("drawing resulting picture")
    img = pixelExtraction.draw(pixelarray, new_width, new_height, verbose=(verbose - 1))
    img.save("FFT_2_input_pixels.png")
    placeImage(canvas, img, CanvasWidth, CanvasHeight)

    return pixelarray


def executeFT(video_path, order, seconds, player, verbose=0):
    """
    This function processes a given looping contour to generate a fourier transfer approximation.
    :param video_path: Defines the path the resulting video should be saved in.
    :param order: Defines how many orders should be shown.
    :param seconds: Defines the length of the resulting video.
    :param player: Defines the player the video should be shown in.
    :param verbose: Defines level of commentary in the console.
    :return: None
    """
    global pixelarray
    array = pixelarray

    # generate FFT
    if verbose > 0:
        print("generating fft")

    frames = seconds * 30

    # execute FFT on pixel array:
    fft = FFT.FFT(array, order, verbose-1)

    # generate mp4
    FFT.makeAnimation(fft, frames, order, video_path, verbose-1)
    player.play(video_path)

