# 引用串口模块
import serial
import time
import numpy as np 

class Cmd_Sender:

    # 数据存储
    Sliding_data = []
    ser = serial.Serial('/dev/ttyUSB0', 921600)
    # 初始化串口

    # 设置角度的命令
    def set_angle(self,angle):
        # ser.write(b'\n')
        # 将角度转换为字符串 保留两位小数
        angle_str = str(round(angle, 1))
        self.ser.write(b'motor set_angle ' + angle_str.encode() + b'\n'+ b'\n')    
        print('\r设置角度为' + angle_str ,end='')

    '''
    递推平均滤波法，输入为新的数据，输出为平均滤波后的数据,滑动窗口长度为 3 
    '''
    def SlidingAverage(self,inputs):
        if len(self.Sliding_data) < 3:
            self.Sliding_data.append(inputs)
            return np.mean(self.Sliding_data)
        else:
            self.Sliding_data.pop(0)
            self.Sliding_data.append(inputs)
            return np.mean(self.Sliding_data)







