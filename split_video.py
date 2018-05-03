import os
import sys
import glob


def split_video():
    p = '/world/data-c5/zhouji_demo_3_15/segmention_dir/river_data/youke_shuizhong_video'
    out_dir = '/world/data-c5/zhouji_demo_3_15/segmention_dir/river_data/youke_jietu'
    for v in glob.glob(os.path.join(p, '*.mp4')):
        print v
        v_name_prefix = os.path.split(v)[-1].split('.mp4')[0]
        cmd_str = 'ffmpeg -i {} -f image2 -vf fps=fps=1 {}_%d.jpg'.format(v, os.path.join(out_dir, v_name_prefix))
        print cmd_str
        os.system(cmd_str)



if __name__ == '__main__':
    split_video()
