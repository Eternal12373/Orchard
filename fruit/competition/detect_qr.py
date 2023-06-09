import cv2
import time
from pyzbar.pyzbar import decode


def qr_decoder(img):
    """
    解码图像内的二维码
    :param img: 图像帧
    :return: 解码数据
    """
    data = []
    
    for barcode in decode(img):
        data = barcode.data.decode('utf-8')
        print(f"\nQRcode detected: {data}\n")
    
    return data


def detect_qr(cam, time_out=5, time_out_en=False):
    """
    解码视野内的二维码，返回正确格式的结果
    :param cam: 摄像头
    :param time_out: 检测超时时间
    :param time_out: 超时时间（默认5s）
    :param time_out_en: 超时允许（默认不允许超时）
    :return: 解码数据
    """
    cap = cv2.VideoCapture(cam)  # 代开摄像头
    print("\n开始识别二维码\n")
    t0 = time.time()  # 初始时间
    flag = 0  # 初始解码情况为失败
    data = []  # 初始化解码内容为空

    while 1:
        # 超时退出
        task_time = time.time() - t0
        if not time_out_en and task_time >= time_out:
            print("\n超时未识别到二维码\n")
            break
            
        ret, img = cap.read()  # 获取摄像头图像帧
        if ret:
            cv2.imshow("qrcode", img)
            # 解二维码
            data = qr_decoder(img)

            if len(data) == 4:  # 解码数据长度判断
                print(f"\nFruit sequence: {data}\n二维码识别结束\n")
                flag = 1
                break
            elif len(data) == 5 and data[-1] == "\n":
                data = data[:4]
                print(f"\nFruit sequence: {data}\n二维码识别结束\n")
                flag = 1
                break	
    
        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            print("\n二维码识别结束\n")
            break
    
    cv2.destroyAllWindows()
    cap.release()
    return flag, data
    
            
if __name__ == '__main__':
    """
    功能测试  每次仅可取注一个功能进行测试
    """
    pass
    """
    image test
    """
#    img = cv2.imread("samples/qrcode.jpg")
#    t0 = time.time()
#    data = qr_decoder(img)
#    t1 = time.time()
#    print("FPS = ", 1 / (t1 - t0))

    """
    video test
    """
#    cam = "samples/detect_qr.mp4"
##    cam = 0
#    data = []
#    ret, data = detect_qr(cam, time_out=5, time_out_en=False)
#    print("QRcode: ", data)
