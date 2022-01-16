# coding=utf-8


# 引用串口模块
import serial
import time


# 初始化串口
ser = serial.Serial('/dev/ttyUSB0', 115200)


# 捕获键盘输入
def getch():
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

# 如果键盘输入为左箭头，使用串口发送左转命令，字符串"motor turn_left 1"
def left():
    ser.write(b'motor turn_left 3')
    # 串口输出回车
    ser.write(b'\n')
    print('左转')
    time.sleep(0.1)


# 如果键盘输入为右箭头，使用串口发送右转命令，字符串"motor turn_right 1"
def right():
    ser.write(b'motor turn_right 3')
    # 串口输出回车
    ser.write(b'\n')
    print('右转')
    # 延时0.1秒
    time.sleep(0.1)

# 主函数
def main():
    # 在控制台输出欢迎信息
    print('欢迎使用车载控制系统')
    # 在控制台输出提示信息
    print('请按下键盘ad方向键控制方向')
    # 在控制台输出提示信息
    print('按下q键退出')
    # 循环
    while True:
        # 如果键盘输入为左箭头，调用left()函数
        if getch() == 'a':
            left()
        # 如果键盘输入为右箭头，调用right()函数
        elif getch() == 'd':
            right()
        # 如果键盘输入为q，退出程序
        elif getch() == 'q':
            break
        # 如果键盘输入为其他，输出提示信息
        else:
            print('请按下键盘ad方向键控制方向')


# 调用主函数
if __name__ == '__main__':
    main()
