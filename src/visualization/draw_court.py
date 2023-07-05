import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Arc

# Function to draw the basketball court lines
# INPUT:
#       - cc_x: x-coordinate of center court
#       - cc_y: y-coordinate of center court
def make_fig(ax=None, color="gray", lw=1, zorder=0, cc_x=0, cc_y=0):   
    if ax is None:
        ax = plt.gca()

    outer = Rectangle((cc_x-47,cc_y-25), width=94, height=50, color=color,
                    zorder=zorder, fill=False, lw=lw)

    # The left and right basketball hoops
    l_hoop = Circle((cc_x-41.65,cc_y+0), radius=.75, lw=lw, fill=False, 
                color=color, zorder=zorder)
    r_hoop = Circle((cc_x+41.65,cc_y+0), radius=.75, lw=lw, fill=False,
                color=color, zorder=zorder)

    # Left and right backboards
    l_backboard = Rectangle((cc_x-43,cc_y-3), 0, 6, lw=lw, color=color,
                        zorder=zorder)
    r_backboard = Rectangle((cc_x+43, cc_y-3), 0, 6, lw=lw,color=color,
                        zorder=zorder)

    # Left and right paint areas
    l_outer_box = Rectangle((cc_x-47, cc_y-8), 19, 16, lw=lw, fill=False,
                        color=color, zorder=zorder)    
    l_inner_box = Rectangle((cc_x-47, cc_y-6), 19, 12, lw=lw, fill=False,
                        color=color, zorder=zorder)
    r_outer_box = Rectangle((cc_x+28, cc_y-8), 19, 16, lw=lw, fill=False,
                        color=color, zorder=zorder)

    r_inner_box = Rectangle((cc_x+28, cc_y-6), 19, 12, lw=lw, fill=False,
                        color=color, zorder=zorder)

    # Left and right free throw circles
    l_free_throw = Circle((cc_x-28, cc_y+0), radius=6, lw=lw, fill=False,
                        color=color, zorder=zorder)
    r_free_throw = Circle((cc_x+28, cc_y+0), radius=6, lw=lw, fill=False,
                        color=color, zorder=zorder)

    # Left and right corner 3-PT lines
    # a represents the top lines
    # b represents the bottom lines
    l_corner_a = Rectangle((cc_x-47, cc_y+22), 14, 0, lw=lw, color=color,
                        zorder=zorder)
    l_corner_b = Rectangle((cc_x-47, cc_y-22), 14, 0, lw=lw, color=color,
                        zorder=zorder)
    r_corner_a = Rectangle((cc_x+33, cc_y+22), 14, 0, lw=lw, color=color,
                        zorder=zorder)
    r_corner_b = Rectangle((cc_x+33, cc_y-22), 14, 0, lw=lw, color=color,
                        zorder=zorder)

    # Left and right 3-PT line arcs
    l_arc = Arc((cc_x-42, cc_y+0), 47.5, 47.5, theta1=292, theta2=68, lw=lw,
            color=color, zorder=zorder)
    r_arc = Arc((cc_x+42, cc_y+0), 47.5, 47.5, theta1=112, theta2=248, lw=lw,
            color=color, zorder=zorder)

    # half_court
    # ax.axvline(470)
    half_court = Rectangle((cc_x+0, cc_y-25), 0, 50, lw=lw, color=color,
                           zorder=zorder)

    hc_big_circle = Circle((cc_x+0, cc_y+0), radius=6, lw=lw, fill=False,
                           color=color, zorder=zorder)
    hc_sm_circle = Circle((cc_x+0, cc_y+0), radius=2, lw=lw, fill=False,
                          color=color, zorder=zorder)

    court_elements = [l_hoop, outer, r_hoop, l_backboard, r_backboard,
                    l_outer_box, l_inner_box, r_outer_box, r_inner_box,
                    l_free_throw, r_free_throw, l_corner_a, l_corner_b,
                    r_corner_a, r_corner_b, l_arc, r_arc, half_court, hc_big_circle,
                    hc_sm_circle]

    # Add the court elements onto the axes
    for element in court_elements:
        ax.add_patch(element)