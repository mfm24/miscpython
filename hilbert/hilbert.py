# mfm 18Mar13 Trying to make a generator that returns values
# from a 2d array in a hilbert curve
import numpy


def make_mapping(m):
    """
    Return a dictionary built up of a single mapping m rotated and flipped.
    The keys are 2 character strings where
    the first is one of [,],u,n and the second is either 'a'nticlockwise or
    'c'lockwise. The values are a list of integer, tuple pair which
    specify how to split up the 4 quadrants and which (shape, direction)
    pair to apply to it.
    The quadrants are
    ---------
    | 0 | 1 |
    ---------
    | 2 | 3 |
    ---------
    """
    quads = [0, 1, 3, 2]  # quadrants in clockwise order
    shapes = ['u', '[', 'n', ']']  # shapes rotated clockwise
    rots = ['a', 'c']  # possible rotations

    def next(item, list, pos=1):
        """
        Given a list and an item, reurns the item in the list
        pos places after the item.
        Wraps around the list at the boundaries
        """
        return list[(list.index(item) + pos) % len(list)]

    other_direction = lambda x: next(x, rots)
    next_quadrant = lambda x: next(x, quads)
    next_shape = lambda x: next(x, shapes)

    def rotate(key):
        rotated_value = [(next_quadrant(quad), next_shape(shape) + dirn)
                         for quad, (shape, dirn) in m[key]]
        shape, dirn = key
        return next_shape(shape) + dirn, rotated_value

    def flip(key):
        flipped_value = list(m[key])
        flipped_value.reverse()
        flipped_value = [(quad, shape+other_direction(dirn))
                         for quad, (shape, dirn) in flipped_value]
        shape, dirn = key
        return shape + other_direction(dirn), flipped_value

    key = m.keys()[0]
    while True:
        key, value = rotate(key)
        if key in m:
            break
        m[key] = value

    for key in m.keys():
        newkey, value = flip(key)
        m[newkey] = value

    return m

hilbert_mapping = make_mapping(
    {'ua': [(0, ']c'), (2, 'ua'), (3, 'ua'), (1, '[c')]})


def apply_mapping(ar, mapping, pos):
    """
    split the 2d array ar into 4 quadrants and call
    apply_mapping recursively for each member of map[pos]
    If ar is 1x1, yield ar
    """
    try:
        y, x = ar.shape[:2]
    except ValueError:
        print ar, ar.shape
    if y <= 1 and x <= 1:
        yield ar[0, 0, ...]
    else:
        # quad indices here are:
        #  0  1
        #  2  3
        # (nb unlike hilbert_v1!)
        first_half = slice(None, x / 2)
        secnd_half = slice(x / 2, None)
        quads = [ar[first_half, first_half, ...],
                 ar[first_half, secnd_half, ...],
                 ar[secnd_half, first_half, ...],
                 ar[secnd_half, secnd_half, ...]]
        for quadrant, newpos in mapping[pos]:
            for x in apply_mapping(quads[quadrant], mapping, newpos):
                yield x


def hilbert(ar):
    for x in apply_mapping(ar, hilbert_mapping, 'ua'):
        yield x


if __name__ == '__main__':
    def showpoints(a, side):
        import Tkinter as tk
        from threading import Thread
        scale = 4
        border = 10
        # we draw points in the order given. We assume the value of the array
        # is it's C style position in a contiguous 2d square array
        w = scale * side + 2 * border
        canvas = tk.Canvas(width=w, height=w)
        canvas.pack(expand=tk.YES, fill=tk.BOTH)
        canvas.create_window(w, w)

        def draw():
            startpos = None
            for p in a:
                nextpos = (border + scale * (p % side),
                           border + scale * (p // side))
                if startpos is None:
                    startpos = nextpos
                else:
                    canvas.create_line(startpos[0], startpos[1],
                                       nextpos[0], nextpos[1])
                startpos = nextpos
        Thread(target=draw).start()
        tk.mainloop()

    s = 128
    x = numpy.arange(s * s).reshape(s, s)

    #xl = list(hilbert(x))
    # print xl
    showpoints(hilbert(x), s)
