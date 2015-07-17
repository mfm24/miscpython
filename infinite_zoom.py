# uses movie py to make a loopable animation, hopefully.
# see http://zulko.github.io/blog/2014/01/23/making-animated-gifs-from-video-files-with-python/
from __future__ import print_function, division
from moviepy.editor import ImageClip, CompositeVideoClip, ColorClip
import os

im_path = os.path.expanduser("mehface.png")

def make_zoom_linearspeed(path=im_path, cx=32, cy=32, scale=10, duration=5, fps=10.0):
    # we zooom using a scale proportional to 1/distance and with a linear speed.
    # problem with this is that if scale is >>2, our foremost image very quickly zooms away
    # so it might make more sense to use a linear scale model (where we scale by a constant
    # fraction each time?)
    ic = ImageClip(path)
    ic.duration = duration
    # we need to go from 1 to scale over duration
    total_frames = int(duration * fps)
    def pos_for_scale_factor(f):
        return cx - cx * f, cy - cy * f
        
    def scale_im(distance, frame_num):
        if distance <= 0.001:
            return ic.set_opacity(0.0).set_duration(0)
        scalef = 1.0  / distance
        print("scalef", scalef)
        # want pos to be 0 when scale = 1, and cx, cy when scale = 0
        ret = ic.set_position(pos_for_scale_factor(scalef)).resize(scalef)
        ret = ret.set_duration(1.5/fps)
        ret = ret.set_start(duration * frame_num / total_frames)
        return ret
        
    def make_zoom_movie(start_d, end_d):
        ret = CompositeVideoClip([scale_im(start_d + (end_d-start_d) * d / (total_frames), d) 
            for d in range(total_frames)], size=ic.size)
        return ret
        
    distance_apart = scale - 1.0
    # we move one from 1 to s
    # and the other from 1 + (1-1/s) to 1
    ret = CompositeVideoClip([
        make_zoom_movie(1.0, 1.0 - distance_apart), 
        make_zoom_movie(1.0 + distance_apart, 1.0)])
    ret.size = ic.size
    return ret
 
def make_zoom_geometric_progression(path=im_path, cx=32, cy=32, scale=10, duration=5, fps=10,
                                    oversample=2.0):
    ic = ImageClip(path).resize(oversample)
    bg = ColorClip((ic.w, ic.h), (0xFF, 0xFF, 0xFF)).set_duration(duration)
    
    ic.duration = duration
    cx *= oversample
    cy *= oversample
    total_frames = int(duration * fps)
    scale_fac = (scale) ** (1.0 / total_frames)
     
    def pos_for_scale_factor(f):
        return cx - cx * f, cy - cy * f
        
    def scale_im(eff_frame_num):
        scalef = (scale_fac ** eff_frame_num) / scale
        print("scalef", scalef)
        # want pos to be 0 when scale = 1, and cx, cy when scale = 0
        ret = ic.set_position(pos_for_scale_factor(scalef)).resize(scalef)
        return ret
        
    def make_zoom_movie(start_d, end_d):
        frames = [scale_im(start_d + (end_d-start_d) * d / (total_frames)) 
            for d in range(total_frames)]
        frames = [f.set_start(duration * i / total_frames).set_duration(1.5/fps)
             for i, f in enumerate(frames)]
        return CompositeVideoClip(frames, size=ic.size)
     
    # we seem to get two multiple frames at the start... 
    # and end sometimes
    ret = CompositeVideoClip([
        bg,
        make_zoom_movie(total_frames, 2.0 * total_frames),
        make_zoom_movie(0, total_frames).fadein(duration/3)
        ]).subclip(1.0/fps, duration)
    ret.size = ic.size
    return ret.resize(1.0/oversample)
    
# do we look at mask?
if __name__=="__main__":
	v = make_zoom_geometric_progression(scale=10, cx=21.5, cy=22.5, duration=1.2, oversample=10, fps=15)
	v.to_gif("mehface_zoom.gif", fps=10)

