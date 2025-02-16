from flask import jsonify, request
import json
import requests
import deepl
from openai import OpenAI
import sqlite3 
from utils import get_location_coordinates, update_location 
user_favorites = {
    '0001': ['大梅沙', '故宫', '天安门'],
    '0002': ['深圳天文台', '拱北口岸'],
    # 更多用户...
}

# SQLite 数据库文件路径
DATABASE = 'loongo.db'

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row  # 使查询结果以字典形式返回
    return db

def process_tuijian_request():
    print("收到调用")
    api_key = '0c8c5707c9a878a15cd1239471072e44'
    response_data = {
        "code": 0,
        "msg": "receving data",
        "data": {
            "result": [
                {
                    "titleTag": "推荐",
                    "pointList": [
                        {
                            "pointName": "孙中山纪念馆",
                            "picUrl": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Former_residence_sunyatsen.JPG/1280px-Former_residence_sunyatsen.JPG",
                            "sugList": ["历史", "人文", "5A级景区"],
                            "location": "xxxx"
                        },
                        {
                            "pointName": "深圳市天文台",
                            "picUrl": "https://weather.sz.gov.cn/img/3/3631/3631290/3562614.jpg",
                            "sugList": ["自然", "徒步", "环境优美"],
                            "location": "xxxx"
                        }
                    ]
                },
                {
                    "titleTag": "附近",
                    "pointList": []
                },
            ]
        }
    }
    coordines = request.args.get('coordines')
    radius = request.args.get('radius', type=int)
    key_words = request.args.get('key_words', type=int)
    if not coordines or not radius:
        return jsonify({'status': 'error', 'message': '缺少必要的参数'}), 400
    updated_response_data = update_location(response_data["data"], api_key, radius, coordines, key_words)
    response_data["data"] = updated_response_data
    response_data["code"] = 200
    return jsonify(response_data)

def process_aichat_request():
    client = OpenAI(
        api_key="sk-rkYmrbXbl6IQ21a7xKfiGLS8pTEWO9gJ6h2t7I47huQdm5uE",
        base_url="https://api.moonshot.cn/v1",
    )
    user_input = request.args.get('ask_question')
    response_data = {
        "code": 0,
        "msg": "receving chat",
        "data": {"result": ""}
    }
    completion = client.chat.completions.create(
        model="moonshot-v1-8k",
        messages=[
            {
                "role": "system",
                "content": "你是一个叫loongo产品的专属小助手，你是一个旅行规划专家，能够帮助用户进行中国旅行过程中的规划，答疑和智能方案，同时在每次问答后也会贴心的给一些小建议"
            },
            {
                "role": "user",
                "content": user_input
            },
        ],
        temperature=0.3,
    )
    answer = completion.choices[0].message.content
    response_data["code"] = 200
    response_data["data"]["result"] = answer
    return jsonify(response_data)

def process_star_request():
    coordines = request.args.get('user_id')
    api_key = '0c8c5707c9a878a15cd1239471072e44'
    print('user_id')
    if coordines in user_favorites:
        favorite_locations = user_favorites[coordines]
        favorites_with_coordinates = {
            location: get_location_coordinates(location, api_key) for location in favorite_locations
        }
        return jsonify(favorites_with_coordinates)
    else:
        return jsonify({'error': 'User not found'}), 404

def process_translate_request():
    response_data = {
        "code": 0,
        "msg": "receive translation",
        "data": {"result": ""}
    }
    coordines = request.args.get('user_id')
    text = request.args.get('text')
    lang = request.args.get('lang')
    auth_key = 'b1092f39-0dbb-4f4d-b960-1adb6cad4982:fx'
    print('user_id')
    translator = deepl.Translator(auth_key)
    result = translator.translate_text(text, target_lang=lang)
    if coordines in user_favorites:
        response_data["data"]["result"] = result.text
        response_data["code"] = 200
        return jsonify(response_data)
    else:
        return jsonify({'error': 'User not found'}), 404

def process_RotePlanSave_request():
    data = request.json
    trip_list = data.get('TripDetails') if data else None
    user_id = data.get('UserId') if data else None
    if not user_id:
        return jsonify({'error': 'UserId is missing in query parameters'}), 400
    if not trip_list:
        return jsonify({'error': 'TripList is missing in request body'}), 400

    db = get_db()
    cursor = db.cursor()
    trip_list_json = json.dumps(trip_list, ensure_ascii=False)
    try:
        cursor.execute('SELECT * FROM AutherUser WHERE UserId = ?', (user_id,))
        user = cursor.fetchone()
        if user:
            cursor.execute('''
                UPDATE AutherUser
                SET TripList = ?
                WHERE UserId = ?
            ''', (trip_list_json, user_id))
            message = 'TripList updated successfully'
        else:
            cursor.execute('''
                INSERT INTO AutherUser (UserId, TripList)
                VALUES (?, ?)
            ''', (user_id, trip_list_json))
            message = 'User created and TripList added successfully'
        db.commit()
        return jsonify({'message': message}), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        db.close()

def process_RotePlanGet_request():
    user_id = request.args.get('UserId')
    if not user_id:
        response = build_response(code=400, msg="UserId is missing in query parameters")
        return jsonify(response), 400

    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute('SELECT TripList FROM AutherUser WHERE UserId = ?', (user_id,))
        user = cursor.fetchone()
        if user:
            trip_list = json.loads(user['TripList'])
            response = build_response(code=200, result=trip_list, msg="Trips retrieved successfully")
            return jsonify(response), 200
        else:
            response = build_response(code=404, msg="User not found")
            return jsonify(response), 404
    except Exception as e:
        response = build_response(code=500, msg=str(e))
        return jsonify(response), 500
    finally:
        cursor.close()
        db.close()

def build_response(code, result=None, msg=None):
    response = {
        "code": code,
        "data": {
            "result": result
        },
        "msg": msg
    }
    return response