import requests

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