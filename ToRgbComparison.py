# what's the best way to convert a 2d float value into
# a rgb uint8 image for showing. We have a few options:
import numpy as np
import time
import sys
no_weave = '--no-weave' in sys.argv

def to_rgb1(im):
    # I think this will be slow
    w, h = im.shape
    ret = np.empty((w, h, 3), dtype=np.uint8)
    ret[:, :, 0] = im
    ret[:, :, 1] = im
    ret[:, :, 2] = im
    return ret

def to_rgb1a(im):
    # This should be fsater than 1, as we only
    # truncate to uint8 once (?)
    w, h = im.shape
    ret = np.empty((w, h, 3), dtype=np.uint8)
    ret[:, :, 2] =  ret[:, :, 1] =  ret[:, :, 0] =  im
    return ret

def to_rgb1b(im):
    # I would expect this to be identical to 1a
    w, h = im.shape
    ret = np.empty((w, h, 3), dtype=np.uint8)
    ret[:, :, 0] = im
    ret[:, :, 1] = ret[:, :, 2] = ret[:, :, 0]
    return ret

def to_rgb2(im):
    # as 1, but we use broadcasting in one line
    w, h = im.shape
    ret = np.empty((w, h, 3), dtype=np.uint8)
    ret[:, :, :] = im[:, :, np.newaxis]
    return ret


def to_rgb3(im):
    # we can use dstack and an array copy
    # this has to be slow, we create an array with 3x the data we need
    # and truncate afterwards
    return np.asarray(np.dstack((im, im, im)), dtype=np.uint8)


def to_rgb3a(im):
    # we can use the same array 3 times, converting to uint8 first
    # this explicitly converts to np.uint8 once and is short
    return np.dstack([im.astype(np.uint8)] * 3)


def to_rgb3b(im):
    # as 3a, but we add an extra copy to contiguous 'C' order
    # data
    return np.dstack([im.astype(np.uint8)] * 3).copy(order='C')

if not no_weave:
    def to_rgb4(im):
        # we use weave to do the assignment in C code
        # this only gets compiled on the first call
        import scipy.weave as weave
        w, h = im.shape
        ret = np.empty((w, h, 3), dtype=np.uint8)
        code = """
        int impos=0;
        int retpos=0;
        for(int j=0; j<Nim[1]; j++)
        {
            for (int i=0; i<Nim[0]; i++)
            {
                unsigned char d=im[impos++];
                ret[retpos++] = d;
                ret[retpos++] = d;
                ret[retpos++] = d;
            }
        }
        """
        weave.inline(code, ["im", "ret"])
        return ret

def to_rgb5(im):
    im.resize((im.shape[0], im.shape[1], 1))
    return np.repeat(im.astype(np.uint8), 3, 2)

"""identical to 4, removing
def to_rgb5(im):
    # we can use the same array 3 times
    return np.dstack([np.asarray(im, dtype=np.uint8)] * 3)

def to_rgb6(im):
    # is [x]*3 any differnt from (x,)*3
    return np.dstack((im.astype(np.uint8),) * 3)
"""

funcs = {x:eval(x) for x in globals() if "to_rgb" in x}
print "testing Numpy v",np.version.version
print "on Python ", sys.version
for size in [64,256,1024,2048]:
    s = np.random.uniform(256, size=(size,size))
    # confirm all functions produce the same output:
    ref = to_rgb1(s)
    times = min(3*10**7/size**2, 10**5) or 1
    print "\n\nFor Size",size,"\n==============="
    for name, func in sorted(funcs.items()):
        out = func(s)
        assert np.array_equal(ref, out)
        if ref.data != out.data:
            print "Array data not in order"
        start = time.time()
        for i in range(times):
            func(s)
        end=time.time()
        print "%s took \t%0.3f ms average for %d times" % (
            name, (1000*(end-start)/times),times)
# see files in this folder for results
