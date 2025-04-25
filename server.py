from flask import Flask, request, jsonify
from flask_cors import CORS  # 如果 Streamlit 和 Flask 不同域，需要打开 CORS

app = Flask(__name__)
CORS(app)

# 全局存一份最新读数
latest = {"temp_c": None, "temp_f": None}

@app.route('/temperature', methods=['POST'])
def temperature_post():
    temp_c = request.form.get('temp_c')
    temp_f = request.form.get('temp_f')
    latest["temp_c"] = temp_c
    latest["temp_f"] = temp_f
    print(f"Current Temp: {temp_c}°C, {temp_f}°F")
    return jsonify({"status": "success"}), 200

@app.route('/temperature', methods=['GET'])
def temperature_get():
    # 直接返回最新读数
    return jsonify(latest), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
