from flask import Flask, request, jsonify

app = Flask(__name__)

# 定义一个路由，用来接收PICO发送过来的温度数据
@app.route('/temperature', methods=['POST'])
def temperature():
    # 如果你是用第一种方法发送数据（即URL编码的数据）
    # 那么可以使用 request.form 来获取数据
    temp_c = request.form.get('temp_c')
    temp_f = request.form.get('temp_f')
    
    # 你也可以打印出来或者存入数据库等
    print(f"Current Temp：{temp_c}°C, {temp_f}°F")
    
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    # 启动服务器，监听所有IP的5000端口
    app.run(host='0.0.0.0', port=80)