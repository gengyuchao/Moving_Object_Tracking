

# -*- coding:utf-8  -*-
 
from xml.sax.handler import all_properties
import cv2
import time
import datetime
import numpy as np 

# 引用串口模块
import Serial_cmd_sender as Cmd_Sender

# 视角范围
view_angle = 70

camera = cv2.VideoCapture(0)
 
if (camera.isOpened()):
    print('Open')
else:
    print('请打开摄像头')
    exit()

#查看视频size
size = (int(camera.get(cv2.CAP_PROP_FRAME_WIDTH)),
        int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT)))

print('size:'+repr(size))

es = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 4)) 
kernel = np.ones((5, 5), np.uint8) 


# 初始化串口
# Cmd_Sender
cmder = Cmd_Sender.Cmd_Sender()

last_time = time.time()


output_angle = 0

center_point_x = 0
center_point_y = 0

frame_pre = None
 
while(1):
    ret, frame_now = camera.read()
    
    frame_now = cv2.flip(frame_now, 1)
    
    gray_lwpCV = cv2.cvtColor(frame_now, cv2.COLOR_BGR2GRAY)
    #gray_lwpCV = cv2.resize(gray_lwpCV, (500, 500))
    gray_lwpCV = cv2.GaussianBlur(gray_lwpCV, (21, 21), 0)
 
    #将当前第一帧作为对比
    if frame_pre is None:
        frame_pre = gray_lwpCV
        continue

    # absdiff把两幅图的差的绝对值输出到另一幅图上面来
    img_delta = cv2.absdiff(frame_pre, gray_lwpCV)
    thresh = cv2.threshold(img_delta, 10, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, es, iterations=2)

    # findContours检测物体轮廓(寻找轮廓的图像,轮廓的检索模式,轮廓的近似办法)
    contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 保存移动物体的最大边界框
    max_box = []

    # 新建一个空的图像
    frame_cc = np.zeros((size[1], size[0], 3), np.uint8)

    # 循环遍历所有的轮廓
    for c in contours:
        # 设置判断的范围
        if cv2.contourArea(c) < 1500:
            continue
        else:
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame_now, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame_now, "Time: {}".format(str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))) ), (10, 20),
                         cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            max_box.append([x, y, x+w, y+h])
            # break
    
    # 对 contours 进行排序，按找到的轮廓的面积进行从大到小排序
    contours_sort = sorted(contours, key=lambda c: cv2.contourArea(c), reverse=True)

    # 显示采集到的小轮廓集合的前5个
    for c in contours_sort[:5]:
        if cv2.contourArea(c) < 500:
            continue
        # 将 c 内部的所有点添加到 frame_cc 中,给不同的轮廓点赋不同随机的颜色
        color = (np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255))
        cv2.drawContours(frame_cc, [c], -1, color, 3)
        # 记录这些轮廓的最小外接圆形
        (x, y), radius = cv2.minEnclosingCircle(c)
        center = (int(x), int(y))
        radius = int(radius)
        # 绘制圆形
        cv2.circle(frame_cc, center, radius, color, 2)
    



    # 计算所max_box坐标列表中最大的矩形区域 （应该是几次采集合集里面）
    if len(max_box) != 0:
        # print(max_box)
        # max_box_x1 = max_box 第一个元素的最小值
        max_box_x1 = min(max_box, key=lambda x: x[0])[0]
        # max_box_y1 = max_box 第一个元素的最小值
        max_box_y1 = min(max_box, key=lambda x: x[1])[1]
        # max_box_x2 = max_box 第一个元素的最大值
        max_box_x2 = max(max_box, key=lambda x: x[2])[2]
        # max_box_y2 = max_box 第一个元素的最大值
        max_box_y2 = max(max_box, key=lambda x: x[3])[3]

        w = max_box_x2 - max_box_x1
        h = max_box_y2 - max_box_y1
        cv2.rectangle(frame_now, (max_box_x1, max_box_y1), (max_box_x1+w, max_box_y1+h), (0, 0, 255), 2)
        
        # 计算当前最大矩形区域的中心点 
        center_point_x = int((max_box_x1+max_box_x2)/2)
        center_point_y = int((max_box_y1+max_box_y2)/2)
        # 显示当前最大矩形区域的中心点 
        cv2.circle(frame_now, (center_point_x, center_point_y), 2, (0, 0, 255), 2)

        # 计算中心点与画面之间的差
        center_x_diff = center_point_x - int(frame_now.shape[1]/2)
        center_y_diff = center_point_y - int(frame_now.shape[0]/2)
        # 归一化
        center_x_diff_one = center_x_diff/float(frame_now.shape[1]/2)
        center_y_diff_one = center_y_diff/float(frame_now.shape[0]/2)

        # 如果中心点不为0，则控制车辆
        if abs(center_point_x) > 50:
            # 打印归一化后的中心点 ，float类型
            # print (center_x_diff)
            # print("center_x_diff_one:", center_x_diff_one, center_y_diff_one)
            output_angle = center_x_diff_one * view_angle + view_angle
            

    # 如果两次命令的间隔小于0.5秒，则不发送
    if (time.time() - last_time) > 0.1:
        output_angle = cmder.SlidingAverage(output_angle)
        cmder.set_angle(output_angle)
        last_time = time.time()

    frame_pre = gray_lwpCV
    cv2.imshow("capture", frame_now)
    cv2.imshow("Frame Delta", img_delta)
    cv2.imshow("frame_cc", frame_cc)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
 
camera.release()
cv2.destroyAllWindows()
