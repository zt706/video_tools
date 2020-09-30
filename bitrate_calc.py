#!/usr/bin/python
# -*- coding:utf-8 -*-

## 计算视频码率

""" 
 @usage: set ffprobe as system path
 @author: zj
 @ pip install matplotlib
 @ set ffprobe bin path as system path
 @ or same path with the script
"""
import os
import sys
import argparse
import subprocess
import pandas as pd
import xml.dom.minidom as xdm
import matplotlib.pyplot as plt

bitexct_cmd = "{exe}  -show_frames -select_streams v -show_entries stream=r_frame_rate,width,height -of xml {input} > {output}"

def run_cmd(command):
	p = subprocess.Popen(command, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)
	stdout, _= p.communicate()
	
	info = stdout.decode('gbk')
	return info

def getKBpsFunc(bits, second):
	return round(bits * 8 / (1024 * second), 3)

def run_ffprobe(in_file, out_file):
	cmd = bitexct_cmd.format(exe='ffprobe', input=in_file, output=out_file)
	if os.path.exists(out_file):
		print('{} exist, delete it'.format(out_file))
		os.remove(out_file) 
	print(cmd)		
	run_cmd(cmd)	  
	
def getVideoInfo(in_file):
	if not os.path.exists(in_file):
		print("{} is not exist".format(in_file))
		return
	root = xdm.parse(in_file)
	itemlist = root.getElementsByTagName("stream")
	item = itemlist[0]
	fps_str = item.getAttribute("r_frame_rate")
	fps_den = fps_str.split('/')[1]
	fps_num = fps_str.split('/')[0]
	width = item.getAttribute("width")
	height = item.getAttribute("height")
	fps = float(fps_num)/float(fps_den)

	return fps, width, height

def getBitWithFPS(in_file, timegop, fps):
	if not os.path.exists(in_file):
		print("{} is not exist".format(in_file))
		return
	root = xdm.parse(in_file)
	itemlist = root.getElementsByTagName("frame")

	time = 0
	size = 0
	totalsize = 0
	totaltime = 0
	bitlist = []
	timelist = []
	duration = 1.0 / float(fps)
	for item in itemlist:
		pkt_size = item.getAttribute("pkt_size")
		time = time + duration
		size = size + int(pkt_size)
		totalsize = totalsize + int(pkt_size)
		totaltime = totaltime + duration
		#bitrate gop set as 5s
		if time > float(timegop):
			bitrate = getKBpsFunc(size, time)
			bitlist.append(bitrate)
			timelist.append(totaltime)
			time = 0
			size = 0
	avg_bitrate = getKBpsFunc(totalsize, totaltime)
	return avg_bitrate, timelist, bitlist  

def DrawBitrateCurve(title, size, timelist, bitlist):	
	fig = plt.figure()
	ax0 = fig.add_subplot(1, 1, 1)
	ax0.set_title(title)
	ax0.set_ylabel('bitrate(kbps)')
	ax0.set_xlabel('time(s)')
	ax0.plot(timelist, bitlist, marker='o')
	
	plt.savefig("{}.png".format(title))
	plt.show()
	plt.close()

def unit_test():
	parser = argparse.ArgumentParser()
	parser.add_argument('--input', '-i', required=True)
	parser.add_argument('--infps', '-fps', required=False, type=float)
	parser.add_argument('--ingops', '-gops', required=False, type=int, default=10)
	parser.add_argument('--csv', '-c', required=False, type=int, choices=range(0, 2), default=0)
	parser.add_argument('--draw', '-d', required=False, type=int, choices=range(0, 2), default=0)	 
	args = parser.parse_args()
	infile = args.input
	ingop = args.ingops

	if not os.path.exists(infile):
		print("{} is not exist".format(infile))
		return		 
	basename = os.path.splitext(os.path.basename(infile))[0]
	outfile = basename + ".xml"
	drawtitle = basename + "(" + str(ingop) + "s)"
	#get size and duration
	run_ffprobe(infile, outfile) 
	#calc time and bitrate
	videofps, width, height = getVideoInfo(outfile)
	if args.infps:
		avgbitrate, timelist, bitlist = getBitWithFPS(outfile, ingop, args.infps)
		print("bitrate: {}kbps setfps:{} fps:{} width:{} height:{}".format(avgbitrate, args.infps, videofps, height, width))
	else:
		avgbitrate, timelist, bitlist = getBitWithFPS(outfile, ingop, videofps)
		print("bitrate: {}kbps fps:{} width:{} height:{}".format(avgbitrate, videofps, height, width))		

	#remove tmp xml file
	os.remove(outfile)
	if args.csv:
		dataframe = pd.DataFrame({'time':timelist, 'bitrate':bitlist})
		dataframe.to_csv("{}_{}_{}x{}_{}kbps.csv".format(basename, videofps, width, height, avgbitrate),index=False,sep=',')
	if args.draw:
		timelen = len(timelist)
		bitlen	= len(bitlist)
		if not (bitlen and timelen) or timelen != bitlen:
			print("error while generate time and bitrate with len (time:{} bitrate:{})".format(timelen, bitlen))
			return False
		DrawBitrateCurve(drawtitle, bitlen, timelist, bitlist)
	
	return True

if __name__=='__main__':
	ret = unit_test()
	exit(ret)
