# image processing:
from PIL import Image, ImageFilter

'''function Blur:'''


def blur(im):
    # blur the image
    # easy method as provided by the pillow library:
    # im = im.filter(ImageFilter.BLUR)
    # controlled method:
    Gaussian_blur_kernel = (1, 4, 6, 4, 1,
                            4, 16, 24, 16, 4,
                            6, 24, 36, 24, 6,
                            4, 16, 24, 16, 4,
                            1, 4, 6, 4, 1)
    return im.filter(ImageFilter.Kernel((5, 5), Gaussian_blur_kernel, 256, 0))


''' Function border: 
# SOURCES:
# https://towardsdatascience.com/canny-edge-detection-step-by-step-in-python-computer-vision-b49c3a2d8123
# https://www.youtube.com/watch?v=uihBwtPIBxM&ab_channel=Computerphile
# https://www.youtube.com/watch?v=sRFM5IEqR2w&ab_channel=Computerphile
# https://en.wikipedia.org/wiki/Feature_detection_(computer_vision)
# https://en.wikipedia.org/wiki/Kernel_(image_processing)
# https://www.youtube.com/watch?v=C_zFhWdM4ic&ab_channel=Computerphile
'''


def border(im, kernel_selection):
    kernel = (0, 0, 0, 0, 0, 0, 0, 0, 0)

    if kernel_selection == 'laplace4':
        # edge detection using laplace1:
        kernel = (-1, -1, -1,
                  -1, 8, -1,
                  -1, -1, -1)
    if kernel_selection == 'laplace2':
        # edge detection using laplace2:
        kernel = (0, -1, 0,
                  -1, 4, -1,
                  0, -1, 0)
    if kernel_selection == 'X sobel':
        # horizontal edge detection using X sobel:
        kernel = (1, 0, -1,
                  2, 0, -2,
                  1, 0, -1)
    if kernel_selection == 'Y sobel':
        # horizontal edge detection using y sobel:
        kernel = (1, 2, 1,
                  0, 0, 0,
                  -1, -2, -1)

    im = im.filter(ImageFilter.Kernel((3, 3), kernel, 1, 0))
    im = im.convert('1')
    w, h = im.size
    im = im.crop((2, 2, w - 2, h - 2))
    return im
