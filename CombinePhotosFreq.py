# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import PIL.Image
%pylab inline

# <codecell>

def gauss_mask(shape, low):
    """
    Return a mask suitable for use on a reduced real FT
    IE zero frequency at 0,0 next at 0,1 1,0 and h-1,0
    """
    h, w = shape
    outw=w/2+1 # if reduced
    # we have full heightfreqs:
    irow = np.fft.fftfreq(h).reshape(h,1)
    # cols are halfed
    icol = np.fft.fftfreq(w)[:outw].reshape(1,outw)
    r = np.exp(-(icol*icol+irow*irow)/(low*low))
    return r

# <codecell>

lowf = np.array(PIL.Image.open(r"C:\Users\Matt\Desktop\stewart_edit.jpg"))
highf = np.array(PIL.Image.open(r"C:\Users\Matt\Desktop\lennon_edit.jpg"))
h,w,_ = lowf.shape

hipass = 1-gauss_mask((w,h), 15.0/768)
lowpass = gauss_mask((w,h), 15.0/768)
lowout=np.fft.irfft2(lowpass*np.fft.rfft2(lowf[:,:,2]))
hiout=np.fft.irfft2(hipass*np.fft.rfft2(highf[:,:,2]))
imsave("patrick_low.png", lowout, cmap='gray')
imsave("lennon_high.png", hiout, cmap='gray')

# <codecell>

imshow(hiout, cmap='gray')

# <codecell>

imshow(lowout, cmap='gray')

# <codecell>

final = lowout+0.5*hiout
imshow(final, cmap='gray')

# <codecell>

imsave("out.png", final, cmap='gray')

