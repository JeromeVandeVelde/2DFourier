from PIL import Image, ImageDraw
import PIL


def firstPixel(im, verbose=0):
    """
    This function detects the first pixel to start the crawler from.
    :param im: Defines the image to search in.
    :param verbose: Defines level of commentary in the console.
    :return: The XY value of the pixel.
    """
    # error at no first pixel
    px = im.load()
    w, h = im.size
    stop = False
    y = 0
    while y < h and not stop:
        x = 0
        while x < w and not stop:
            if px[x, y] != 0:
                pixel = [x, y]
                stop = True
            x = x + 1
        y = y + 1
    if verbose > 0:
        print("base pixel = ", pixel)
    return pixel


def pixels(im, radiusLimit, minimumPoints, verbose=0):
    """
    This function detect all pixels neighboring the base pixels.
    :param im: Defines the image to search in.
    :param RadiusLimit: Defines the limit of the search radius in pixels.
    :param minimumPoints: Defines the minimum amount of points the crawler should return.
    :param verbose: Defines level of commentary in the console.
    :return: An array consisting of all XY coordinates of the detected contour.
    """
    # init radius
    if radiusLimit == 0:
        if verbose > 0:
            print("Radius limit set to infinite")
        radiusLimit = 99999

    if verbose > 0:
        print("picture size:", im.size)
        im.show()
    # find base pixel
    base = firstPixel(im, verbose=verbose)
    # create array to place found pixels in
    pixelarray = [base]

    # outwards radiation algorithm:
    amount = 0
    pixel = base
    start = True

    while pixel != base or start:
        start = False
        # the crawler hasn't finished the loop:
        pixel = findNextPixel(im, base, pixel, pixelarray, minimumPoints, radiusLimit, verbose)
        pixelarray.append(pixel)

        if pixel == base and verbose > 0:
            print("crawler has made a loop")

        amount = amount + 1
        if amount > 9999:
            # To many pixels
            if verbose > 0:
                print("failed successfully, to many pixels found")
            break

    return pixelarray


def findNextPixel(im, base, pixel, pixelarray, minimumPoints, radiusLimit,verbose=0):
    """
    This functions return the closest neighboring pixel for a given pixel that isn't listed in the pixelarray
    :param im: Defines the image to search in.
    :param base: Define the base pixel the crawler started from.
    :param pixel: Defines the pixel to search from.
    :param pixelarray: Defines the points already detected.
    :param minimumPoints: Defines the minimum amount of points the crawler should return.
    :param RadiusLimit: Defines the limit of the search radius in pixels.
    :param verbose: Defines level of commentary in the console.
    :return: The XY value of a pixel.
    """
    # based on the base pixel, return pixel that is not base while the minimumpoint isn't reached in the img
    radius = 1
    px = im.load()
    picture_width, picture_height = im.size
    while radius < radiusLimit:
        # search north to north-east
        x = 0
        y = -radius
        while x < radius and pixel[0] + x < picture_width-1:                                                              # move right until radius is reached or the border of the picture
            if px[pixel[0] + x, pixel[1] + y] != 0:                                                                     # when pixel, control if new.
                if newpixel(base, pixelarray, pixel[0] + x, pixel[1] + y, minimumPoints, verbose=verbose):              # if new pixel:
                    return [pixel[0] + x,pixel[1] + y]                                                                  # return found pixel
                else:
                    x = x + 1
            else:
                x = x + 1

        # search north-east to south-east:
        while y < radius and pixel[1]+y < picture_height-1:                                                               # move down until radius is reached or the border of the picture
            if px[pixel[0] + x, pixel[1] + y] != 0:                                                                     # when pixel, control if new.
                if newpixel(base, pixelarray, pixel[0] + x, pixel[1] + y, minimumPoints, verbose=verbose):              # if new pixel:
                    return [pixel[0] + x, pixel[1] + y]                                                                  # return found pixel
                else:
                    y = y + 1
            else:
                y = y + 1
        # search south-east to south-west
        while x > -radius and pixel[0]+x > 1:                                                                           # move left until radius is reached or the border of the picture
            if px[pixel[0] + x, pixel[1] + y] != 0:                                                                     # when pixel, control if new.
                if newpixel(base, pixelarray, pixel[0] + x, pixel[1] + y, minimumPoints, verbose=verbose):              # if new pixel:
                    return [pixel[0] + x, pixel[1] + y]                                                                  # return found pixel
                else:
                    x = x - 1
            else:
                x = x - 1
        # search south-west to north-west
        while y > -radius and pixel[1]+y > 1:                                                                           # move up until radius is reached or the border of the picture
            if px[pixel[0] + x, pixel[1] + y] != 0:                                                                     # when pixel, control if new.
                if newpixel(base, pixelarray, pixel[0] + x, pixel[1] + y, minimumPoints, verbose=verbose):              # if new pixel:
                    return [pixel[0] + x, pixel[1] + y]                                                                  # return found pixel
                else:
                    y = y - 1
            else:
                y = y - 1
        # search north-west to north
        while x < 0:                                                                                                   # move right until null is reached again
            if px[pixel[0] + x, pixel[1] + y] != 0:                                                                     # when pixel, control if new.
                if newpixel(base, pixelarray, pixel[0] + x, pixel[1] + y, minimumPoints, verbose=verbose):              # if new pixel:
                    return [pixel[0] + x,pixel[1] + y]                                                                  # return found pixel
                else:
                    x = x + 1
            else:
                x = x + 1

        # nothing in this proximity, increase radius
        radius = radius + 1
        if verbose > 1:
            print("radius = ", radius)
        if radius > picture_height and radius > picture_width:
            # all pictures are found, return base
            if verbose > 0:
                print("failed to find the required amount of pixels")
            return base
    if radius >= radiusLimit:
        if verbose > 0:
            print("no pixels found. increase radius perhaps, or decrease pixel amounts")
        return base


def newpixel(base, pixelarray, x, y, minimumPoints, verbose=0):
    """
    This function defines if a found pixel is already detected before or not.
    Should the base pixel be found, a go-ahead to break the operation can be given if the required amount of points was found.
    :param base: Define the base pixel the crawler started from.
    :param pixelarray: Defines the points already detected.
    :param x: Defines the X-value of the found pixel
    :param y: Defines the Y-value of the found pixel
    :param minimumPoints: Defines the minimum amount of points the crawler should return.
    :param verbose: Defines level of commentary in the console.
    :return: A True or false.
    """
    for pixel in pixelarray:
        # if pixel is new but not base
        if (pixel == [x,y] and pixel != base):
            if verbose > 1:
                print("old pixel found: ")
            return False
        # if pixel is base, but array is to short
        if ([x,y] == base and len(pixelarray) < minimumPoints):
            if verbose > 0:
                print("base found, but to soon")
            return False
    if verbose > 0:
        print("new pixel found", len(pixelarray), "/", minimumPoints, ": ", [x,y])
    return True


def rescale_array(pixelarray, requestedpoints, verbose=0):
    """
    This function rescales the amount of points in an array to a given value.
    :param pixelarray: Defines the array to be rescaled
    :param requestedpoints: Defines the amount of points needed
    :param verbose: Defines level of commentary in the console.
    :return: the new pixel array
    """
    trimratio = len(pixelarray)/requestedpoints
    trimmedpixelarray = [pixelarray[0]]

    if trimratio < 1:
        if verbose > 0:
            print("no trimming required")
        return pixelarray

    if verbose > 0:
        print("requested points = ", requestedpoints)
        print("points found:", len(pixelarray))
        print("trim ratio:", trimratio)

    # Trimming
    for i in range(requestedpoints):
        x = int((i+1)*trimratio)
        trimmedpixelarray.append(pixelarray[x-1])

    if verbose > 0:
        print("new length:", len(trimmedpixelarray))

    return trimmedpixelarray


def rescale_picture(pixelarray, scalefactor, verbose=0):
    """
    This function returns a scaled pixel array rescaled to a new given factor.
    :param pixelarray: Defines the pixel array to rescale.
    :param scalefactor: Defines the scale factor to resolve.
    :param verbose: Defines level of commentary in the console.
    :return: The scaled pixel array.
    """
    if verbose > 0:
        print("scalefactor: ", scalefactor)

    return_pixel_array = []
    for i in range(len(pixelarray)):
        x = int(pixelarray[i][0] * scalefactor)
        y = int(pixelarray[i][1] * scalefactor)
        return_pixel_array.append([x, y])
        if verbose > 0:
            print(i, ": ", return_pixel_array[i])

    return return_pixel_array


def draw(pixelarray, width, height, verbose=0):
    """
    This function return a picture drawn with the detected contour.
    :param pixelarray: Defines the pixel array to draw.
    :param width: Defines the width to draw
    :param height: Defines the height to draw
    :param verbose: Defines level of commentary in the console.
    :return: The resulting image
    """
    if verbose > 0:
        print("received dimentions are: ", width, "x", height)
    im = PIL.Image.new(mode="RGB", size=(int(width), int(height)))
    px = im.load()
    draw = ImageDraw.Draw(im)
    px[pixelarray[0][0], pixelarray[0][1]] = 255, 255, 255

    for i in range(len(pixelarray)-1):  # reform to len()
        draw.line((pixelarray[i][0], pixelarray[i][1], pixelarray[i + 1][0], pixelarray[i + 1][1]), fill=(0,256,256))
        px[pixelarray[i][0], pixelarray[i][1]] = (255, 255, 255)

    return im


