import cv2
import time
import os
from datetime import datetime

def capture_rtsp_stream(rtsp_url: str, interval_sec: int = 2, save_dir: str = "sample_image_demo"):
    """
    每隔 interval_sec 秒从 RTSP 拉流截图一次，并覆盖保存为 sample_image_model_fridge/6.jpg。

    参数：
    - rtsp_url: 摄像头 RTSP 地址
    - interval_sec: 截图时间间隔（秒）
    - save_dir: 截图保存的文件夹路径（默认 sample_image_model_fridge）
    """
    # 自动创建保存目录
    os.makedirs(save_dir, exist_ok=True)

    print("🔌 正在尝试连接摄像头...")
    cap = cv2.VideoCapture(rtsp_url)
    time.sleep(2)

    # 跳过缓存帧
    for i in range(5):
        ret, _ = cap.read()
        print(f"尝试读取第{i+1}帧...")

    try:
        while True:
            ret, frame = cap.read()
            if ret:
                # 始终保存为 sample_image_model_fridge/6.jpg
                filename = os.path.join(save_dir, "6.jpg")
                cv2.imwrite(filename, frame)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 📸 最新截图已保存为：{filename}")
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
    capture_rtsp_stream(rtsp_url, interval_sec=2, save_dir="sample_image_demo")
