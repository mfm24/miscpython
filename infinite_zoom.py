# uses movie py to make a loopable animation, hopefully.
# see http://zulko.github.io/blog/2014/01/23/making-animated-gifs-from-video-files-with-python/
from __future__ import print_function, division
from moviepy.editor import ImageClip, CompositeVideoClip, ColorClip
import os

im_path = os.path.expanduser("mehface.png")


def make_zoom_movie(src, scales, fps, center):
    cx, cy = center
    def pos_for_scale_factor(f):
        return cx - cx * f, cy - cy * f
    ret = []
    for frame, scale in enumerate(scales):
        new_frame = (src
                     .set_position(pos_for_scale_factor(scale))
                     .resize(scale)
                     .set_start(duration * frame / len(scales))
                     .set_duration(1.0/fps))
        ret.append(new_frame)
    return CompositeVideoClip(ret, size=src.size)
            
def make_zoom(scale_func, path=im_path, cx=32, cy=32, scale=10, duration=5, fps=10,
                                    oversample=2.0):
    ic = ImageClip(path).resize(oversample)
    bg = ColorClip((ic.w, ic.h), (0xFF, 0xFF, 0xFF)).set_duration(duration)
    
    ic.duration = duration
    cx *= oversample
    cy *= oversample
    total_frames = int(duration * fps)
        
    def zoom_between_frames(startf, endf):
        scales = [scale_func(startf + f * (endf - startf) / total_frames)
                  for f in range(total_frames)]
        return make_zoom_movie(ic, scales, fps, (cx, cy))
     
    # we seem to get two multiple frames at the start... 
    # and end sometimes
    ret = CompositeVideoClip([
        bg,
        zoom_between_frames(total_frames, 2.0 * total_frames),
        zoom_between_frames(0, total_frames)
        ])
    ret.size = ic.size
    # ret.duration = duration
    return ret.resize(1.0/oversample)
    
# do we look at mask?
if __name__=="__main__":
    fps = 15
    duration = 1.2
    def geom(scale, frames):
        # want scale to change by a factor of scale over
        # frames, and to be 1.0 at frames. 
        def get_scale_for_frame(f):
            return (scale ** (f / frames - 1))
        return get_scale_for_frame
            
    v = make_zoom(geom(10, fps*duration), cx=21.5, cy=22.5, duration=1.2, oversample=4.0, fps=fps)
    v.to_gif("mehface_zoom.gif", fps=fps)

