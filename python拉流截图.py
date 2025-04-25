import cv2
import time
from datetime import datetime

def capture_rtsp_stream(rtsp_url: str, interval_sec: int = 60):
    """
    每隔 interval_sec 秒从 RTSP 拉流截图一次，直到手动停止。

    参数：
    - rtsp_url: 摄像头 RTSP 地址（记得把密码里的 @ 改成 %40）
    - interval_sec: 截图时间间隔（秒）
    """
    print("🔌 正在尝试连接摄像头...")
    cap = cv2.VideoCapture(rtsp_url)

    # 等待摄像头建立连接
    time.sleep(2)

    # 跳过缓存帧
    for i in range(5):
        ret, _ = cap.read()
        print(f"尝试读取第{i+1}帧...")

    try:
        while True:
            ret, frame = cap.read()
            if ret:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.jpg"
                cv2.imwrite(filename, frame)
                print(f"[{timestamp}] 📸 截图已保存：{filename}")
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ 无法从摄像头获取图像。")

            time.sleep(interval_sec)

    except KeyboardInterrupt:
        print("\n🛑 程序手动停止。")

    finally:
        cap.release()
        print("✅ 摄像头连接已关闭。")

# 示例用法
if __name__ == "__main__":
    rtsp_url = "rtsp://admin:13758255798%40Yjs@192.168.31.64:554/h264/ch1/main/av_stream"
    capture_rtsp_stream(rtsp_url, interval_sec=300)  # 每隔 300 秒截图一次
