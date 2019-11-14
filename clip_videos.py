import sys
import os

"""
clip one video to some short clips
"""

if __name__ == "__main__":
    print("xxxxxxxxxxxxxxxx")
    vName = sys.argv[1]
    outName = "F:\\youtube-download\\1080-clip\\" + str(vName)[:-4]
    startTime = 0
    endTime = 0
    length = int(sys.argv[2]) * 60
    i=0
    while endTime <= length:
        i= i + 1
        endTime= startTime + 3*60
        str_cmd = "ffmpeg.exe -i " +  "\"" + vName + "\"" + " -ss " + str(startTime)  + " -to " + str(endTime)  + " -an -vcodec copy " +  "\"" + outName + "_clip_" + str(i) + ".mp4" + "\""
        startTime = endTime
        print(str_cmd)
        os.system(str_cmd)
