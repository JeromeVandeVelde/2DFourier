import Coordinates
import numpy as np
from tqdm import tqdm  # for progress bar
from scipy.integrate import quad_vec  # for calculating definite integral
from math import tau
import cmath
import matplotlib.pyplot as plt  # for plotting and creating figures
import matplotlib.animation as animation  # for compiling animation and exporting video


def generateComplexNumber(t, t_sample, x_list, y_list):
    """
    Gives x + iy at any time t
    :param t: time
    :param t_sample: sample of all the times(here angle)
    :param x_list: x-coordinates
    :param y_list: y-coordinates
    :return: x + iy at any time t
    """
    return np.interp(t, t_sample, x_list + 1j * y_list)


def FFT(pixelarray, order, verbose=0):
    """
    This function calculates the fourier coefficient of a pixel array.
    :param pixelarray: 2D array of pixel coordinates.
    :param order: order of the fourier transform: order = 2*vectors+1
    :param verbose: Defines level of commentary in the console.
    :return: 9D array with freq, coeff, angles, range x-axis, range y-axis, x-coord, y-coord, the angles  from 0 to 2pi (t_coor)
    """
    coord = Coordinates.coord(pixelarray)
    x_lim = coord[3]
    y_lim = coord[4]
    x_list = coord[0]
    y_list = coord[1]
    t_coor = coord[2]

    if verbose > 0:
        print("order = ", order)

    # function to generate x+iy at given time t
    coeffs = []  # coeffs
    frequenties = []
    stralen = []
    hoeken = []
    pbar = tqdm(total=(order * 2 + 1))

    for n in range(-order, order + 1):
        # calculate definite integration from 0 to 2*PI
        # formula is given in readme

        coef = 1 / tau * \
               quad_vec(lambda t: generateComplexNumber(t, t_coor, x_list, y_list) * np.exp(-n * t * 1j), 0, tau,
                        limit=100, full_output=1)[0]
        print(coef)
        coeffs.append(coef)
        frequenties.append(n)
        stralen.append(abs(coef))
        hoek = (cmath.phase(coef) * 360) / (2 * np.pi)
        hoeken.append(hoek)
        pbar.update(1)

    pbar.close()
    if verbose > 0:
        print("completed generating coefficients.")

    # converting list into numpy array
    Array = np.array((frequenties, coeffs, stralen, hoeken, x_lim, y_lim, x_list, y_list, t_coor))
    return Array


def makeAnimation(fft, frames, order, filename, verbose=0):
    """
    This function makes an animation of a given fft series.
    :param fft: Defines the complex values required for the animation.
    :param frames: defines the amount of frames the animation will contain.
    :param order: defines the amount of circles the animation contains.
    :param filename: Defines the location the animation is saved in.
    :param verbose: Defines level of commentary in the console.
    :return: filename of mp4 file
    """
    spf = 20  # miliseconds per frame

    xlim_data = fft[4]
    ylim_data = fft[5]

    """ What is this for?"""
    draw_x = []
    draw_y = []

    # make figure for animation
    fig, ax = plt.subplots()
    # circles of the epicycles
    circles = [ax.plot([], [], 'r-')[0] for i in range(-order, order + 1)]
    # circle_lines are radius of each circles
    circle_lines = [ax.plot([], [], 'b-', linewidth=0.8)[0] for i in range(-order, order + 1)]
    # drawing is plot of final drawing
    drawing, = ax.plot([], [], 'k-', linewidth=0.8)
    # original drawing
    orig_drawing, = ax.plot([], [], 'g-', linewidth=0.5)
    # to fix the size of figure so that the figure does not get cropped/trimmed
    ax.set_xlim(xlim_data[0] - 50, xlim_data[1] + 50)
    ax.set_ylim(ylim_data[0] - 50, ylim_data[1] + 50)
    # hide axes
    ax.set_axis_off()
    # to have symmetric axes
    ax.set_aspect('equal')
    if verbose > 0:
        print("compiling animation ...")
    # set number of frames
    pbar = tqdm(total=frames)

    time = np.linspace(0, tau, num=frames)
    anim = animation.FuncAnimation(fig, make_frame, frames=frames,
                                   fargs=(
                                   time, fft, order, circle_lines, draw_x, draw_y, drawing, orig_drawing, circles, pbar,
                                   verbose - 1),
                                   interval=spf)  # animation matplotlib function
    # Set up formatting for the video file
    Writer = animation.writers['ffmpeg']
    writer = Writer(fps=30, metadata=dict(artist='timur'), bitrate=1800)
    anim.save(filename, writer=writer)
    pbar.close()
    if verbose > 0:
        print("mp4 Completed")

    return filename


def make_frame(i, time, fft, order, circle_lines, draw_x, draw_y, drawing, orig_drawing, circles, pbar, verbose=0):
    """
    This function draws the vector field for each time interval t.
    :param i: Defines the index
    :param time: Defines the time
    :param fft: Defines the fft
    :param order: Defines the orders
    :param circle_lines: Defines the cicle lines
    :param draw_x: Defines the X values
    :param draw_y: Defines the Y values
    :param drawing: Defines the drawing
    :param orig_drawing: Defines the original drawing
    :param pbar: Defines the concolse loding bar
    :param verbose: Defines level of commentary in the console.
    :return: None
    """
    coeffs = fft[1]
    stralen = fft[2]
    hoeken = fft[3]
    x_list = fft[6]
    y_list = fft[7]

    # get t from time
    t = time[i]

    # exponential term to be multiplied with coefficient
    # this is responsible for making rotation of circle
    exp_term = []
    for n in range(-order, order + 1):
        exp_term.append(np.exp(n * t * 1j))
    exp_term = np.array(exp_term)
    # sort the terms of fourier expression
    coeffs = sort_coeff(coeffs * exp_term, order)  # coeffs*exp_term makes the circle rotate.
    # coeffs itself gives only direction and size of circle

    # split into x and y coefficients
    x_coeffs = np.real(coeffs)
    y_coeffs = np.imag(coeffs)

    if order == 0:
        x_coeffs = x_coeffs * 350
        y_coeffs = y_coeffs * 350

    # center points for fisrt circle
    center_x = 0
    center_y = 0
    # make all circles i.e epicycle
    for i, (x_coeff, y_coeff) in enumerate(zip(x_coeffs, y_coeffs)):
        # calculate radius of current circle
        r = np.linalg.norm([x_coeff, y_coeff])  # similar to magnitude: sqrt(x^2+y^2)

        # draw circle with given radius at given center points of circle
        # circumference points: x = center_x + r * cos(theta), y = center_y + r * sin(theta)
        theta = np.linspace(0, tau, num=50)  # theta should go from 0 to 2*PI to get all points of circle
        x, y = center_x + r * np.cos(theta), center_y + r * np.sin(theta)
        circles[i].set_data(x, y)

        # draw a line to indicate the direction of circle
        x, y = [center_x, center_x + x_coeff], [center_y, center_y + y_coeff]
        circle_lines[i].set_data(x, y)

        # calculate center for next circle
        center_x, center_y = center_x + x_coeff, center_y + y_coeff

        # center points now are points from last circle
        # these points are used as drawing points

    # center points now are points from last circle
    # these points are used as drawing points
    draw_x.append(center_x)
    draw_y.append(center_y)

    # draw the curve from last point
    drawing.set_data(draw_x, draw_y)  # DEZE TEKENT DE CURVE MET draw_x en draw_y DE PUNTEN

    # draw the real curve
    orig_drawing.set_data(x_list, y_list)

    # update progress bar
    pbar.update(1)


def sort_coeff(coeffs, order):
    """
    Sort the coefficients in order 0, 1, -1, 2, -2,...
    :param coeffs: array of coefficients
    :param order: Defines the orders to be drawn
    :return: the sorted array of coefficients
    """
    new_coeffs = [coeffs[order]]
    for i in range(1, order + 1):
        new_coeffs.extend([coeffs[order + i], coeffs[order - i]])
    # new_coeffs.reverse()
    return np.array(new_coeffs)
