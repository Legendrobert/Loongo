# main.py
from flask import Flask, request, jsonify
# 导入第三方库
import requests
from openai import OpenAI

app = Flask(__name__)

#默认用户收藏地点
user_favorites = {
    '0001': ['大梅沙', '故宫', '天安门'],
    '0002': ['深圳天文台', '拱北口岸'],
    # 更多用户...
}


@app.route('/Loongo/tuijian', methods=['GET'])
def handle_post():
    print("收到调用")
    api_key = '0c8c5707c9a878a15cd1239471072e44'
    response_data = {
        "code": 0,
        "msg": "receving data",
        "data":
            {"result": [
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
                    "pointList": [
                    ]
                },
            ]
            }
    }
    coordines = request.args.get('coordines')
    radius = request.args.get('radius', type=int)
    key_words = request.args.get('key_words', type=int)
    if not coordines or not radius:
        return jsonify({'status': 'error', 'message': '缺少必要的参数'}), 400
    # 调用函数获取周边旅游景点信息
    # 获取地点经纬度
    updated_response_data = update_location(response_data["data"], api_key, radius, coordines, key_words)

    response_data["data"] = updated_response_data
    response_data["code"] = 200
    return jsonify(response_data)


@app.route('/Loongo/aichat', methods=['GET'])
def handle_get():
    client = OpenAI(
        api_key="sk-rkYmrbXbl6IQ21a7xKfiGLS8pTEWO9gJ6h2t7I47huQdm5uE",
        base_url="https://api.moonshot.cn/v1",
    )

    user_input = request.get_data(as_text=True)  # 获取请求体的文本内容
    response_data = {
        "code": 0,
        "msg": "receving chat",
        "data":
            {"result": ""}
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
    response_data["data"]["result"] = answer  # 填充answer到result中
    return jsonify(response_data)  # 返回response_data


@app.route('/Loongo/star', methods=['GET'])
def handle_star():
    coordines = request.args.get('user_id')
    api_key = '0c8c5707c9a878a15cd1239471072e44'
    # 检查用户ID是否存在
    print('user_id')
    if coordines in user_favorites:
        # 获取用户收藏的地点名称列表
        favorite_locations = user_favorites[coordines]

        # 使用get_location_coordinates函数获取每个地点的坐标
        favorites_with_coordinates = {
            location: get_location_coordinates(location, api_key) for location in favorite_locations
        }

        # 返回包含地点名称和坐标的JSON对象
        return jsonify(favorites_with_coordinates)
    else:
        # 如果用户ID不存在，返回错误信息
        return jsonify({'error': 'User not found'}), 404


def get_location_coordinates(place_name, api_key):
    # 高德地图地理编码API的URL
    url = "https://restapi.amap.com/v3/geocode/geo"
    # 构建请求参数
    params = {
        "address": place_name,
        "key": api_key
    }
    # 发送GET请求
    response = requests.get(url, params=params)
    # 解析响应内容
    data = response.json()
    # 检查状态码
    if data['status'] == '1' and data['geocodes']:
        # 获取第一个结果的经纬度
        location = data['geocodes'][0]['location']
        return location
    else:
        print("未能找到地点或发生错误")
        return None


def get_surrounding_tourist_attractions(location, radius, api_key, key_words="风景名胜"):
    # 高德地图周边搜索API的URL
    url = "https://restapi.amap.com/v3/place/around"
    # 构建请求参数
    params = {
        "location": location,
        "keywords": key_words,
        "radius": radius,
        "key": api_key,
        "limit": 5
    }
    # 发送GET请求
    response = requests.get(url, params=params)
    # 解析响应内容
    data = response.json()
    # 检查状态码
    if data['status'] == '1':
        return data
    else:
        return {'status': 'error', 'message': '未能找到地点或发生错误'}


def update_location(response_data, api_key, radius, Coordines, key_word):
    result4surrondings = get_surrounding_tourist_attractions(Coordines, radius, api_key, key_word)
    try:
        for result in response_data['result']:
            if result["titleTag"] == "推荐":
                if 'pointList' in result:
                    for point in result['pointList']:
                        point_name = point['pointName']
                        location = get_location_coordinates(point_name, api_key)
                        if location:
                            point['location'] = location
            if result["titleTag"] == "附近":
                if 'pointList' in result:
                    for pois in result4surrondings['pois']:
                        new_point = {
                            "pointName": pois["name"],
                            "picUrl": None,
                            "sugList": pois["type"].split(";"),
                            "location": pois["location"]
                        }
                        # 添加到附近
                        result["pointList"].append(new_point)
    except KeyError as e:
        print(e)
    if not response_data['result'][1]['pointList']:
        del response_data['result'][1]
    return response_data


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
