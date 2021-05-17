import numpy as np
from math import tau
import matplotlib.pyplot as plt


def coord(pixelarray):
    """
    Calculates the x and y coordinates
    :param pixelarray: 2D array with the x and y coordinates
    :return: 5D array with x-coord, y-coord, the angles(t_list), range of x-axis and y-axis
    """
    x_coor = [i[0] for i in pixelarray]
    y_coor = [i[1] for i in pixelarray]

    t_coor = np.linspace(0, tau, len(x_coor))  # now we can relate f(t) -> x,y

    x_list = x_coor - np.mean(x_coor)
    y_list = y_coor - np.mean(y_coor)
    for i in range(len(y_list)):
        if y_list[i] < 0 or y_list[i] > 0:
            y_list[i] = y_list[i] * -1

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(x_list, y_list)

    # later we will need these data to fix the size of figure
    xlim_data = plt.xlim()
    ylim_data = plt.ylim()

    # plt.show()
    lists_coor = np.array((x_list, y_list, t_coor, xlim_data, ylim_data))
    return lists_coor

    #####  coord(pixelarray)[0] = x_list
    #####  coord(pixelarray)[1] = y_list
    #####  coord(pixelarray)[2] = t_list
    #####  coord(pixelarray)[3] = x_lim
    #####  coord(pixelarray)[4] = y_lim
