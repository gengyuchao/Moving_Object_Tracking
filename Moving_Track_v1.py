# coding=utf-8

import cv2
import numpy as np
from numpy.core.numeric import count_nonzero
from numpy.lib.function_base import flip


cap = cv2.VideoCapture(0);

frame_width = int( cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height =int( cap.get( cv2.CAP_PROP_FRAME_HEIGHT))

# 等待输入回车 #
ready = input("Press Enter to start")  # 如果是 python2  ready = raw_input("Press Enter to start")

# 获取背景图像
ret, background = cap.read()
# 背景翻转
background = cv2.flip(background, +1)

while cap.isOpened():

    ret, frame_now = cap.read()
    # 第一帧图像水平翻转
    frame_now = cv2.flip(frame_now,1)

    # 使用当前图像与背景图像做差
    diff_bkg = cv2.absdiff(frame_now, background)
    # 将与背景图像做差不相等的位置标记为mask
    mask = cv2.cvtColor(diff_bkg, cv2.COLOR_BGR2GRAY)
    # 将 mask 的差值大于阈值的位置标记为mask
    mask[mask < 50] = 0

    # 去除掉孤立的点
    mask = cv2.erode(mask, None, iterations=2)

    # 将 mask 中小块的未标记填充
    mask = cv2.dilate(mask, None, iterations=5)

    # 显示 mask 位置原来的图像
    cv2.imshow("mask", mask)

    # 将 frame_now 中 mask 位置的图像放到 frame_changed 中
    frame_changed = cv2.bitwise_and(frame_now, frame_now, mask=mask)
    center_point_x = 0 
    center_point_y = 0
    # 如果 mask 部分的面积大于总面积的1/40，则认为是移动的物体
    if count_nonzero(mask) > (frame_now.size / 40):
        # 计算移动物体的位置
        M = cv2.moments(mask)
        # 计算移动物体的中心位置
        center_point_x = int(M['m10']/M['m00'])
        center_point_y = int(M['m01']/M['m00'])
    # 在 frame_changed 中画出移动物体的位置
    cv2.circle(frame_changed, (center_point_x, center_point_y), 10, (0, 0, 255), -1)

    # 显示 frame_changed
    cv2.imshow("frame_changed", frame_changed)

    if cv2.waitKey(40) == 27:
        break

cv2.destroyAllWindows()
cap.release()
