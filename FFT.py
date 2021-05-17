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
    # TODO: orders should be circles. define how many orders are required for n circles. return the circles from big to small.
    # TODO: if verbose, print progress comments
    # TODO: recomment parameters
    """
    calculates the fourier coefficient
    :param pixelarray: 2D array of pixel coordinates
    :param order: order of the fourier transform: order = 2*vectors+1
    :return: 9D array with freq, coeff, angles, range x-axis, range y-axis, x-coord, y-coord, the angles  from 0 to 2pi (t_coor)
    """
    coord = Coordinates.coord(pixelarray)
    x_lim = coord[3]
    y_lim = coord[4]
    x_list = coord[0]
    y_list = coord[1]
    t_coor = coord[2]

    # function to generate x+iy at given time t
    c = []
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
        c.append(coef)
        frequenties.append(n)
        stralen.append(abs(coef))
        hoek = (cmath.phase(coef) * 360) / (2 * np.pi)
        hoeken.append(hoek)

        pbar.update(1)

    pbar.close()
    print("completed generating coefficients.")

    # converting list into numpy array
    Array = np.array((frequenties, c, stralen, hoeken, x_lim, y_lim, x_list, y_list, t_coor))
    return Array


def makeAnimation(fft, frames, order, filename, verbose=0):
    # TODO: fit image in canvas better, a lot of space is wasted
    # TODO: if verbose, print progress comments
    # TODO: recomment parameters
    """
    calls make_frame function with an interval of 20ms with parameters time and c
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
    # circle_lines are radius of each circles
    circle_lines = [ax.plot([], [], 'b-', linewidth=0.8)[0] for i in range(-order, order + 1)]
    # drawing is plot of final drawing
    drawing, = ax.plot([], [], 'k-', linewidth=0.8)
    # original drawing
    orig_drawing, = ax.plot([], [], 'g-', linewidth=0.5)
    # to fix the size of figure so that the figure does not get cropped/trimmed
    ax.set_xlim(xlim_data[0] - 300, xlim_data[1] + 300)
    ax.set_ylim(ylim_data[0] - 300, ylim_data[1] + 300)
    # hide axes
    ax.set_axis_off()
    # to have symmetric axes
    ax.set_aspect('equal')

    print("compiling animation ...")
    # set number of frames
    pbar = tqdm(total=frames)

    time = np.linspace(0, tau, num=frames)
    anim = animation.FuncAnimation(fig, make_frame, frames=frames,
                                   fargs=(time, fft, order, circle_lines, draw_x, draw_y, drawing, orig_drawing, pbar, verbose-1),
                                   interval=spf)  # animation matplotlib function
    # Set up formatting for the video file
    Writer = animation.writers['ffmpeg']
    writer = Writer(fps=30, metadata=dict(artist='timur'), bitrate=1800)
    anim.save(filename, writer=writer)
    pbar.close()
    print("mp4 Completed")

    return filename


def make_frame(i, time, fft, order, circle_lines, draw_x, draw_y, drawing, orig_drawing, pbar, verbose=0):
    # TODO: if verbose, print progress comments ( only very little)
    # TODO: recomment parameters
    """
    draws the vectors for each time t (i.e. angle)
    :param i: the index of the time list
    :param time: the time list
    :param coeffs: array of coefficients
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
    coeffs = sort_coeff(coeffs * exp_term, order, verbose-1)  # coeffs*exp_term makes the circle rotate.
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
    for i in range(len(coeffs)):
        r = stralen[i]  # abs(coeffs[i]) #straal
        # draw circle with given radius at given center points of circle
        # circumference points: x = center_x + r * cos(theta), y = center_y + r * sin(theta)
        theta = np.linspace(hoeken[i], hoeken[i] + tau,
                            num=40)  # theta should go from 0 to 2*PI to get all points of circle in 40 punten verdeeld
        x = center_x + r * np.cos(theta)
        y = center_y + r * np.sin(theta)
        # circles[i].set_data(x, y)

        # draw a line to indicate the direction of circle
        x = [center_x, center_x + x_coeffs[i]]
        y = [center_y, center_y + y_coeffs[i]]
        circle_lines[i].set_data(x, y)

        # calculate center for next circle
        center_x = center_x + x_coeffs[i]
        center_y = center_y + y_coeffs[i]

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


def sort_coeff(coeffs, order, verbose=0):
    # TODO: if verbose, print progress comments
    # TODO: recomment parameters
    """
    Sort the coefficients in order 0, 1, -1, 2, -2,...
    :param coeffs: array of coefficients
    :return: the sorted array of coefficients
    """
    new_coeffs = [coeffs[order]]
    for i in range(1, order + 1):
        new_coeffs.extend([coeffs[order + i], coeffs[order - i]])
    # new_coeffs.reverse()
    return np.array(new_coeffs)
