import os,sys
import cv2 
import numpy as np


"""
制作超分 sr 和 对应的 lr 的数据集(帧对齐)，基本流程如下：
1) sr video -> sr yuv ->sr frames
2) sr video -> lr yuv -> (x264 编码 maxbitrate=4M)lr h264 -> lr yuv -> lr frames 
"""

class VideoCaptureYUV:
    def __init__(self, filename, size):
        self.height, self.width = size
        self.frame_len = self.width * self.height * 3 / 2 
        self.f = open(filename, 'rb')
        self.shape = (int(self.height*1.5), self.width)

    def read_raw(self):
        try:
            raw = self.f.read(self.frame_len)
            yuv = np.frombuffer(raw, dtype=np.uint8)
            yuv = yuv.reshape(self.shape)
        except Exception as e:
            print str(e)
            return False, None
        return True, yuv 

    def read(self):
        ret, yuv = self.read_raw()
        if not ret:
            return ret, yuv 
        #bgr = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_NV21)
        bgr = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_I420, 3)
        return ret, bgr 


def get_yuv(flv, yuv, height, width):
    size = str(width) + 'x' + str(height)
    cmd_2_yuv = "ffmpeg -i %s -s %s  -pix_fmt yuv420p -y %s" % (flv, size, yuv)
    print('ffmpeg cmd_2_yuv: %s ' % cmd_2_yuv)
    os.system(cmd_2_yuv)

def yuv_clip(yuv_path, clip_dir, size=(720,1080), clip_inter=1, img_prefix="sr", img_surfix=".png"): 
    cap = VideoCaptureYUV(yuv_path, size)
    img_num = 0 
    saved_num = 0 
    while 1:
        ret, frame = cap.read()
        if ret:
            img_num += 1
            if img_num % clip_inter != 0:
                continue 
            saved_num += 1
                        img_name = "%s/%s_%06d%s" % (clip_dir, img_prefix, saved_num, img_surfix)
            #cv2.imwrite(img_name, frame, [int(cv2.IMWRITE_PNG_COMPRESSION), 0])
            cv2.imwrite(img_name, frame)
            if saved_num % 10 == 0:
                pass
                print("save %s" % (img_name))
        else:
            break
    return img_num, saved_num

def yuv_2_h264(yuv_path, h264_path, max_bit=1200):
    cmd_yuv_2_264 = "x264 -o %s %s --vbv-maxrate %s --vbv-bufsize %s" % (h264_path, yuv_path, max_bit, max_bit)
    print('x264 cmd_yuv_2_264: %s ' % cmd_yuv_2_264)
    os.system(cmd_yuv_2_264)

def main(sr_flv, sr_yuv, sr_shape, lr_yuv, lr_h264, lr_yuv_new, lr_shape, lr_max_bit, sr_clip_dir, lr_clip_dir, clip_inter=1, img_surfix=".png"):
    """
    clip_inter: Take one frame every x frames
    """

    # fisrt: get sr clip from sr yuv file
    height, width = sr_shape[1], sr_shape[0]            # h,w
    get_yuv(sr_flv, sr_yuv, height, width)
    img_num_sr, saved_num_sr = yuv_clip(sr_yuv, sr_clip_dir, (height, width), clip_inter, "sr", img_surfix)
    print("sr total img: %s, saved img: %s" % (img_num_sr, saved_num_sr))

    # second: get lr clip from encoded lr yuv file
    height, width = lr_shape[1], lr_shape[0]            # h,w 
    lr_max_bit = 1200
    get_yuv(sr_flv, lr_yuv, height, width)
    yuv_2_h264(lr_yuv, lr_h264, lr_max_bit)
    get_yuv(sr_flv, lr_yuv_new, height, width)
    img_num_lr, saved_num_lr = yuv_clip(lr_yuv, lr_clip_dir, (height, width), clip_inter, "lr", img_surfix)
    print("lr total img: %s, saved img: %s" % (img_num_lr, saved_num_lr))

    if img_num_sr != img_num_lr:
        print("\nwarning: video(%s) sr total img(%s) != lr total img(%s) \n" % (sr_flv, img_num_sr, img_num_lr))
    elif saved_num_sr != saved_num_lr:
        print("\nwarning: video(%s) lr saved img(%s) != lr saved img(%s) \n" % (sr_flv, saved_num_sr, saved_num_lr))

if __name__ == '__main__':
    """
    sr video: sr_flv
    sr clip dir: mkdir ./sr_clip
    lr clip dir: mkdir ./lr_clip
        """

    sr_flv = './outdoor_test.flv'
    sr_shape = (1920,1080)
    lr_shape = (960,540)
    lr_max_bit = 1200
    clip_inter = 30             # Take one frame every x frames 
    img_surfix = ".jpg"
    origin_vname = sr_flv.split('/')[-1].split('.')[0]

    sr_yuv = './%s_sr_%sx%s.yuv' % (origin_vname, sr_shape[0], sr_shape[1])
    lr_yuv = './%s_lr_%sx%s.yuv' % (origin_vname, lr_shape[0], lr_shape[1])
    lr_yuv_new = './%s_lr_%sx%s_new.yuv' % (origin_vname, lr_shape[0], lr_shape[1])
    lr_h264 = './%s_lr_%sx%s.h264' % (origin_vname, lr_shape[0], lr_shape[1])

    sr_dir = os.path.join('./sr_clip', origin_vname)
    lr_dir = os.path.join('./lr_clip', origin_vname)
    os.system("cd %s && rm -rf %s && mkdir %s " % ('./sr_clip', origin_vname, origin_vname))
    os.system("cd %s && rm -rf %s && mkdir %s " % ('./lr_clip', origin_vname, origin_vname))

    main(sr_flv, sr_yuv, sr_shape, lr_yuv, lr_h264, lr_yuv_new, lr_shape, lr_max_bit, sr_dir, lr_dir, clip_inter, img_surfix)
