# main.py
import json

from flask import Flask, request, jsonify
# 导入第三方库
from handlers4app import (
    process_tuijian_request,
    process_aichat_request,
    process_star_request,
    process_translate_request,
    process_RotePlanSave_request,
    process_RotePlanGet_request
)

app = Flask(__name__)

@app.route('/Loongo/tuijian', methods=['GET'])
def handle_post():
    return process_tuijian_request()

@app.route('/Loongo/aichat', methods=['GET'])
def handle_get():
    return process_aichat_request()

@app.route('/Loongo/star', methods=['GET'])
def handle_star():
    return process_star_request()

@app.route('/Loongo/translate', methods=['GET'])
def handle_translate():
    return process_translate_request()

@app.route('/Loongo/RotePlanSave', methods=['POST'])
def handle_RotePlkan():
    return process_RotePlanSave_request()

@app.route('/Loongo/RotePlanGet', methods=['GET'])
def handle_RotePlanGet():
    return process_RotePlanGet_request()



if __name__ == '__main__':
    # kimi的api-key
    # sk-rkYmrbXbl6IQ21a7xKfiGLS8pTEWO9gJ6h2t7I47huQdm5uE
    # 使用示例
    try:
        print("服务启动中...")
        app.run(host="0.0.0.0", port=3000, debug=True)
    except Exception as e:  # 修改为 Exception 以捕获所有异常
        print(f"发生错误: {e}")  # 打印错误信
    ##测试用澳门大三巴的location是113.552458,22.200815
