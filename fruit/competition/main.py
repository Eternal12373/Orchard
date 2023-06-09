from detect_turn import detect_turn
from detect_qr import detect_qr
from go_series import *
from motion import arm_standby, arm_scout
from serial_communication import serial_communicate

arm_standby(arm_middle)  # 机械臂待命位
chassis_reset = serial_communicate("0")  # 底盘重置
input("确认打开服务器后按回车\n>>>")
input("按回车运行\n>>>")

cam = 0  # 调用摄像头

traffic_position_get = serial_communicate("1")  # 前往1号交叉点
if traffic_position_get:
    arm_scout(arm_middle)  # 机械臂抬起
    turn = detect_turn(cam, sample_time=9, time_out=20, time_out_en=False)  # 读转向标识
    arm_standby(arm_middle)  # 机械臂待命位
    if turn == 1:  # 识别结果左转
        ret = serial_communicate(turn_left)
    elif turn == 3:  # 识别结果右转
        ret = serial_communicate(turn_right)

qr_position_get = serial_communicate("2")  # 前往2号交叉点
flag_qr = 0  # 初始化解码成功标志位为失败
fruit_seq = [0, 0, 0, 0]  # 初始化解码结果
if qr_position_get:
    arm_scout(arm_middle)  # 机械臂抬起
    flag_qr, fruit_seq = detect_qr(cam, time_out=5, time_out_en=False)  # 读二维码
    arm_standby(arm_middle)  # 机械臂待命位

fruit_tree_basket = np.zeros((3, 4))  # 创建3行4列空表，第1行存采摘区果号，第2行存树号，第3行存放置区果号
fruit_tree_basket[1] = [1, 2, 3, 4]  # 初始化树号

if flag_qr:  # 解到二维码
    fruit_tree_basket[0] = list(fruit_seq)  # 解码结果记录到第1行
    fruit_tree_basket = fruit_tree_basket.T[np.lexsort(-fruit_tree_basket[::-1, :])].T  # 按果号(第1行)倒序排列整张映射表
    print("\n树号： ", fruit_tree_basket[1])
    print("果号： ", fruit_tree_basket[0], "\n")

    # 前往4号果对应的树（fruit_tree_basket2行1列），此时树上应有2个黄果，20s内抓1个，退回交叉点待命
    grab_ok = go_grab_retreat(cam, tree=int(fruit_tree_basket[1][0]),
                              color=yellow, circle_number=2, grab_time_out=20)
    num_4 = 1 if grab_ok else 2  # 更新黄球计数(存在缺陷，即碰落会导致树上只有1，但计数为2不变，可考虑参考detect_ball.py Line85 自行修改)
    
    fruit_tree_basket[2], _ = go_detect_seq(cam, mode=1)   # 放置区测序，记录到第3行(测序时会将抓到的4号果对应放置)

else:  # 未解到二维码
    fruit_tree_basket[0], grab_ok = go_detect_seq(cam, mode=0)  # 前往采摘区测序
    num_4 = 1 if grab_ok else 2  # 更新黄球计数

    fruit_tree_basket = fruit_tree_basket.T[np.lexsort(-fruit_tree_basket[::-1, :])].T  # 按果号(第1行)倒序排列整张映射表
    print("\n树号： ", fruit_tree_basket[1])
    print("果号： ", fruit_tree_basket[0], "\n")

    fruit_tree_basket[2], _ = go_detect_seq(cam, mode=1)  # 放置区测序

# 抓4号果剩下的1个黄球
try:  # 防止测序中未识别到4号而报错
    basket = np.where(fruit_tree_basket[2] == 4)[0][0]  # 测序结果列表中数字4所在的位置，即对应篮号
    grab_ok = go_grab_retreat(cam, tree=int(fruit_tree_basket[1][0]),
                              color=yellow, circle_number=num_4, grab_time_out=20)
    if grab_ok:
        go_put_in_basket(int(basket))
    # 抓4号果第1颗白球
    grab_ok = go_grab_retreat(cam, tree=int(fruit_tree_basket[1][0]),
                              color=white, circle_number=1, grab_time_out=20)
    if grab_ok:
        go_put_in_basket(int(basket))
except:  # 报错则跳过4号
    pass
   
# 4号已放置完，取、放3,2,1
for i in range(3):  # 树
    print("\nTree: ", 3-i, "\n")
    try:  # 防止测序中未识别到该种而报错
        basket = np.where(fruit_tree_basket[2] == 3 - i)[0][0]  # 对应篮号
    except:  # 报错则跳过该种
        continue
    num = 2  # 树上黄果计数
    for j in range(2):  # 抓取两次黄果
        grab_ok = go_grab_retreat(cam, tree=int(fruit_tree_basket[1][i + 1]),
                                  color=yellow, circle_number=num, grab_time_out=20)
        if grab_ok:
            num = 1  # 更新黄球计数(存在缺陷，即碰落会导致树上只有1，但计数为2不变，可考虑参考detect_ball.py Line85 自行修改) 
            go_put_in_basket(int(basket))
    # 白果
    grab_ok = go_grab_retreat(cam, tree=int(fruit_tree_basket[1][i + 1]),
                              color=yellow, circle_number=1, grab_time_out=20)
    if grab_ok:
        go_put_in_basket(int(basket))

# 去终点
park = serial_communicate("8")
