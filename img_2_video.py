def img_2_video(root_path, video_out_dir):
    
    if not os.path.isdir(video_out_dir):
        os.mkdir(video_out_dir)
        
    imgs = os.listdir(root_path)
    img_num = len(imgs)
    
    assert img_num >= 5
    
    v_name_prefix = imgs[0].split('.jpg')[0]
    idx = v_name_prefix.rindex('_')
    v_name = v_name_prefix[:idx]
    video_name =  v_name + '.mp4'
    
    # 调整帧率的参数 -r 要加在 -i 前面
    cmd_str = 'ffmpeg -f image2 -r 3 -i ' + root_path + '/' + v_name + '_%d.jpg '  + video_out_dir + '/' + video_name
    print 'cmd str == ', cmd_str
    os.system(cmd_str)


#img_2_video(result_out_root, './video_out')
