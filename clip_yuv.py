import os,sys
import cv2
import numpy as np

"""
clip yuv file to png(jpg) images

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
            if saved_num > 30: break
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

if __name__ == "__main__":
    yuv_path = '/workspace/mengdongwei/dishi_test/dishi_sr_yuv_backup/1080_lol_006_cut2_dishi.yuv'
    clip_dir = './clip_xiangui'
    size=(2160,3840)
    yuv_clip(yuv_path, clip_dir, size)
    
    
