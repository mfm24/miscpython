# 2013-04-03 Trying Code && Beer at Substantial.
# what happens if we take the pixels in an image,
# rearrange using a hilbert curve, then save as png?
# is there any increase (or decrease) in compression
try:
    import Image  # needs PIL for this
except ImportError:
    from PIL import Image

import hilbert
import numpy as np
from StringIO import StringIO


def to_hilbert(im):
    im_dat = np.asarray(im)
    w, h = im.size

    if w & (w - 1) != 0 or h & (h - 1) != 0:
        print "Warning, dimensions", w, h, "not powers of two!"

    # let's create a new image for the transformed data
    imout = Image.new(im.mode, (w, h))
    imout_dat = imout.load()

    imout_dat_pos = 0
    for px in hilbert.hilbert(im_dat):
        imout_dat[imout_dat_pos % w, imout_dat_pos // w] = tuple(px)
        imout_dat_pos += 1
    return imout


def from_hilbert(im):
    w, h = im.size

    if w & (w - 1) != 0 or h & (h - 1) != 0:
        print "Warning, dimensions", w, h, "not powers of two!"

    # let's create a new image for the transformed data
    imout = Image.new(im.mode, (w, h))
    imout_dat = imout.load()

    imout_dat_pos = 0
    im_dat = im.load()
    # we create a matrix of x and y positions which we pass in
    xy = np.dstack(np.mgrid[0:h, 0:w])
    for (px, py) in hilbert.hilbert(xy):
        imout_dat[int(py), int(px)] = tuple(
            im_dat[imout_dat_pos % w, imout_dat_pos // w])
        imout_dat_pos += 1
    return imout


def to_image(im):
    w, h = im.size
    # let's create a new image for the transformed data
    imout = Image.new(im.mode, (w, h))
    imout_dat = imout.load()

    imout_dat_pos = 0
    for px in im.getdata():
        imout_dat[imout_dat_pos % w, imout_dat_pos // w] = tuple(px)
        imout_dat_pos += 1
    return imout


def test(file):
    im = Image.open(file)
    imout = to_image(im)
    assert(all(map(lambda (x, y): x == y, zip(im.getdata(), imout.getdata()))))
    imout = to_hilbert(im)
    imout = from_hilbert(imout)
    assert(all(map(lambda (x, y): x == y, zip(im.getdata(), imout.getdata()))))


if __name__ == '__main__':
    # we can test this on the 512x512 pngs in testpngs folder in bash with:
    # for f in testpngs/*; do python hilbert_png.py -t -f GIF -u "$f"; done;
    # this test, using GIF format, with unprocessing too 
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help='The file to load')
    parser.add_argument(
        "--test", "-t", action='store_true',
        help="Doesn't write files, just calculates the sizes")
    parser.add_argument(
        "--reversehilbert", "-r", action='store_true',
        help="Reverses the effect of the program. Will restore the original image")
    parser.add_argument(
        "--unprocessed", "-u", action='store_true',
        help="Write an unprocessed file as well as a processed one.")
    parser.add_argument(
        "--outfile", "-o",
        help="File to write to.", default="out")
    parser.add_argument(
        "--unprocessedoutfile", "-uo",
        help="File to write unprocessed data to.")
    parser.add_argument(
        "--format", "-f",
        help="The format(s) to use. Seperate by semicolons to select more than one", default="png")
    args = parser.parse_args()
    infile = args.file  # "out.png"
    im = Image.open(infile)
    print infile
    # test("out.png")
    def save(func, name, formats):
        imout = func(im)
        for format in formats.split(';'):
            if args.test:
                s = StringIO()
            else:
                ofile = name
                ofile += "." + format
                s = open(ofile, 'wb')

            imout.save(s, format=format)
            if args.test:
                print "%s,%s,%d,Kb" % (func.__name__, format, s.len / 1024)
            s.close()

    func = to_hilbert if not args.reversehilbert else from_hilbert
    save(func, args.outfile, args.format)
    if args.unprocessed:
        save(to_image, args.unprocessedoutfile, args.format)
