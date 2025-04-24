import cv2
import time
from datetime import datetime

# 替换为你的摄像头实际信息
rtsp_url = "rtsp://admin:13758255798@Yjs@192.168.1.64:554/h264/ch1/main/av_stream"

# 打开视频流
cap = cv2.VideoCapture(rtsp_url)

# 等待摄像头建立连接
time.sleep(2)

# 连续跳过缓存帧
for i in range(5):
    ret, frame = cap.read()
    print(f"尝试读取第{i+1}帧...")

# 开始定时截图
try:
    while True:
        ret, frame = cap.read()
        if ret:
            # 当前时间命名截图文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.jpg"
            cv2.imwrite(filename, frame)
            print(f"[{timestamp}] 截图已保存：{filename}")
        else:
            print("⚠️ 无法从摄像头获取图像。")

        # 等待 60 秒再截图
        time.sleep(60)

except KeyboardInterrupt:
    print("\n程序手动停止。")

finally:
    cap.release()
