from tkinter import ttk
from tkinter import *
import gui

from tkvideoplayer import tkvideo

# console output :
verbose = 0

# predefined values
minimumPoints = 20
RadiusLimit = 0
requestedpoints = 500
new_width = 600
kernel_list = ['laplace4', 'laplace2', 'X sobel', 'Y sobel']
order = 20  # AANTAL CIRKELS: order = divided by two rounded down
Seconds = 5
video_path = "epicycle.mp4"

# Gui Vars:
CanvasWidth = 300
CanvasHeight = 300
vidWidth = 500
vidHeight = 500

# design gui:
root = Tk()
root.title("Two dimentional Fourier Transformation")  # replace title
root.geometry(str(CanvasWidth * 4 + 50) + "x" + str(CanvasHeight + vidHeight + 100))

# create a main frame
main_frame = Frame(root)
main_frame.pack(fill=BOTH, expand=1)

# create a canvas
my_canvas = Canvas(main_frame)
my_canvas.pack(side=LEFT, fill=BOTH, expand=1)

# Add A Scrollbar To The Canvas
my_scrollbar = ttk.Scrollbar(main_frame, orient=VERTICAL, command=my_canvas.yview)
my_scrollbar.pack(side=RIGHT, fill=Y)

# Configure The Canvas
my_canvas.configure(yscrollcommand=my_scrollbar.set)
my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all")))

# Create ANOTHER Frame INSIDE the Canvas
content = Frame(my_canvas)
# Add that New frame To a Window In The Canvas
my_canvas.create_window((0, 0), window=content, anchor="nw")

# padding
p1 = Label(content, width=3)
p1.grid(row=0, column=0, sticky=W, pady=2)
p1 = Label(content, height=60)
p1.grid(row=20, column=4, sticky=W, pady=2)
# gui variables
edgeThinning = BooleanVar()
kernel_var = StringVar(content)
kernel_var.set(kernel_list[0])

# Title
l_title = Label(content, text="Two dimentional Fourier Transformation", font=("Times", "24", "bold italic"))
l_title.grid(row=0, column=1, columnspan=5, sticky=W, pady=2)

# Input                 (row 1->3

c_in = Canvas(content, width=CanvasWidth, height=CanvasHeight)
c_in.grid(row=1, column=1, columnspan=3, rowspan=1, sticky=W, pady=2)
c_in.configure(bg='grey')

l_in1 = Label(content, text="filename", width=27, anchor="e")
l_in1.grid(row=2, column=1, columnspan=2, sticky=W, pady=2)
b_in1 = Button(content, text='select file', command=lambda: gui.upload(c_in, l_in1, CanvasWidth, CanvasHeight))
b_in1.grid(row=2, column=3, sticky=W, pady=2)

l_in2 = Label(content, text="New width:", width=27, anchor="e")
l_in2.grid(row=3, column=1, columnspan=2, sticky=W, pady=2)
t_in2 = Text(content, height=1, width=10, font=("Courier", 10, "bold"))
t_in2.grid(row=3, column=3, columnspan=1, sticky=W, pady=2)
t_in2.insert(INSERT, new_width)

text = "With this GUI, you can import a picture and play with it to try and find a contour approximate by a fourier ser"
text = text + "ies. With the use of the button ‘select file’ you can choose a file on your computer to start the analys"
text = text + "ation. This Application will generate outputs on your current location. The ratio will remain the same, "
text = text + "but the size of the image will be defined by the width. We recommend taking visually simple images. By t"
text = text + "his we mean images with clearly defined features. This will help you find borders more clearly and gener"
text = text + "ate better results by extension. "
l_text1 = Label(content, text=text, wraplength=500, justify=LEFT)
l_text1.grid(row=1, column=4, columnspan=2, sticky=W, pady=2)

# Border detection      (row 4->8)

l_bd1 = Label(content, text="Step 1: Border detection", width=27, anchor="w", font=("Helvetica", 16, "bold"))
l_bd1.grid(row=4, column=1, columnspan=3, sticky=W, pady=2)

text = "For the first part of the process, you must find the borders of the image. By using different kernels you will find different results. Try some out until you are satisfied with the result. Edge thinning will reduce noise over the picture. Depending on the picture, edge thinning can be an advantage or an inconvenience. "
l_text1 = Label(content, text=text, wraplength=300, justify=LEFT)
l_text1.grid(row=5, column=5, sticky=W, pady=2)

l_bd2 = Label(content, text="Border detection kernel:", width=27, anchor="e")
l_bd2.grid(row=5, column=1, columnspan=2, sticky=W, pady=2)
m_bd = OptionMenu(content, kernel_var, *kernel_list)
m_bd.grid(row=5, column=3, columnspan=1, rowspan=1, sticky=W, pady=2)

l_bd3 = Label(content, text="Edge thinning:", width=27, anchor="e")
l_bd3.grid(row=7, column=1, columnspan=2, sticky=W, pady=2)
c1 = Checkbutton(content, onvalue=1, offvalue=0, variable=edgeThinning)
c1.grid(row=7, column=3, columnspan=1, rowspan=1, sticky=W, pady=2)
edgeThinning.set(True)

c_bd = Canvas(content, width=CanvasWidth, height=CanvasHeight)
c_bd.grid(row=4, column=4, columnspan=1, rowspan=5, sticky=W, pady=2)
c_bd.configure(bg='grey')

b_bd = Button(content, text='run', command=lambda: gui.executeDB(l_in1['text'], c_bd, kernel_var.get(), edgeThinning.get(), CanvasWidth, CanvasHeight))
b_bd.grid(row=8, column=1, sticky=W, pady=2)

# Contour detection      (row 8->13)

l_cd1 = Label(content, text="Step 2: Contour detection", width=27, anchor="w", font=("Courier", 16, "bold"))
l_cd1.grid(row=9, column=1, columnspan=3, sticky=W, pady=2)

text = "In this step we will run a crawler over the picture. The highest point on your picture will be the starting point of the crawler over the picture. By setting the radius limit as a non-zero positive number, you can limit the distance between two jumps of the crawler. By setting a minimum amount of points to be returned, you can let the crawler search for more pixels, and let it cover a bigger part of the image if needed. Finally, by requesting a higher amount of points to be returned, you can increase the resolution of the found contour."
l_text1 = Label(content, text=text, wraplength=300, justify=LEFT)
l_text1.grid(row=10, column=5, sticky=W, pady=2)

l_cd2 = Label(content, text="minimum points detected:", width=27, anchor="e")
l_cd2.grid(row=10, column=1, columnspan=2, sticky=W, pady=2)
t_cd2 = Text(content, height=1, width=10, font=("Courier", 10, "bold"))
t_cd2.grid(row=10, column=3, columnspan=1, sticky=W, pady=2)
t_cd2.insert(INSERT, minimumPoints)

l_cd3 = Label(content, text="Crawler Radius limit:")
l_cd3.grid(row=11, column=1, columnspan=4, sticky=W, pady=2)
t_cd3 = Text(content, height=1, width=10, font=("Courier", 10, "bold"))
t_cd3.grid(row=11, column=3, columnspan=1, rowspan=1, sticky=W, pady=2)
t_cd3.insert(INSERT, RadiusLimit)

l_cd4 = Label(content, text="request output points:")
l_cd4.grid(row=12, column=1, columnspan=4, sticky=W, pady=2)
t_cd4 = Text(content, height=1, width=10, font=("Courier", 10, "bold"))
t_cd4.grid(row=12, column=3, columnspan=1, rowspan=1, sticky=W, pady=2)
t_cd4.insert(INSERT, requestedpoints)

b_cd = Button(content, text='run',
              command=lambda: gui.executeCB(c_cd, int(t_cd3.get("1.0", END)), int(t_cd2.get("1.0", END)),
                                            int(t_cd4.get("1.0", END)), int(t_in2.get("1.0", END)), CanvasWidth,
                                            CanvasHeight))
b_cd.grid(row=13, column=1, sticky=W, pady=2)

c_cd = Canvas(content, width=CanvasWidth, height=CanvasHeight)
c_cd.grid(row=9, column=4, columnspan=9, rowspan=5, sticky=W, pady=2)
c_cd.configure(bg='grey')

# Fourier transfer (row 14->18)

l_ft1 = Label(content, text="Step 3: Fourier Transform", width=27, anchor="w", font=("Courier", 16, "bold"))
l_ft1.grid(row=14, column=1, columnspan=3, sticky=W, pady=2)

text = "For the last step, start by defining the amount of circles you want in the approximation of your edge. This is dependent on the order (= 2x circles). The higher the amount of circles, the closer the fourier series will be to the original contour. You can also specify the playback speed of the loop in seconds."
l_text1 = Label(content, text=text, wraplength=300, justify=LEFT)
l_text1.grid(row=15, column=4, columnspan=2, sticky=W, pady=2)

l_ft2 = Label(content, text="Fourier order:")
l_ft2.grid(row=15, column=1, columnspan=4, sticky=W, pady=2)
t_ft2 = Text(content, height=1, width=10, font=("Courier", 10, "bold"))
t_ft2.grid(row=15, column=3, columnspan=1, rowspan=1, sticky=W, pady=2)
t_ft2.insert(INSERT, order)

l_ft3 = Label(content, text="Duration of the loop (s):")
l_ft3.grid(row=16, column=1, columnspan=4, sticky=W, pady=2)
t_ft3 = Text(content, height=1, width=10, font=("Courier", 10, "bold"))
t_ft3.grid(row=16, column=3, columnspan=1, rowspan=1, sticky=W, pady=2)
t_ft3.insert(INSERT, Seconds)

b_ft = Button(content, text='run',
              command=lambda: gui.executeFT(video_path, int(t_ft2.get("1.0", END)), int(t_ft3.get("1.0", END)), player))
b_ft.grid(row=18, column=1, sticky=W, pady=2)

video_label = Label(content, anchor="n")
video_label.grid(row=19, column=4, rowspan=10, columnspan=2, sticky=W, pady=2)
player = tkvideo(video_label, loop=1, size=(int(CanvasHeight * 2), int(CanvasHeight * 2)))

root.mainloop()
