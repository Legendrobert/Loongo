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
    process_RotePlanGet_request,
    process_loc_detail
)

app = Flask(__name__)

@app.route('/Loongo/tuijian', methods=['GET'])
#地点推荐
def handle_post():
    return process_tuijian_request()

@app.route('/Loongo/aichat', methods=['GET'])
#ai智能语音聊天
def handle_get():
    return process_aichat_request()


@app.route('/Loongo/loc_detail', methods=['GET'])
#ai本地内容推荐
def handle_loc():
    return process_loc_detail()

@app.route('/Loongo/star', methods=['GET'])
#收藏接口
def handle_star():
    return process_star_request()

@app.route('/Loongo/translate', methods=['GET'])
#翻译接口
def handle_translate():
    return process_translate_request()

@app.route('/Loongo/RotePlanSave', methods=['POST'])
#路径规划保存
def handle_RotePlkan():
    return process_RotePlanSave_request()

@app.route('/Loongo/RotePlanGet', methods=['GET'])
#路径规划获取
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
