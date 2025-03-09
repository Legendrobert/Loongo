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
    lon, lat = map(float, Coordines.split(','))
    spots = get_osm_tourist_spots_with_keywords(lat, lon, radius)
    #result4surrondings = get_surrounding_tourist_attractions(Coordines, radius, api_key, key_word)
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
                    # for pois in spots['pois']:
                    #     new_point = {
                    #         "pointName": pois["name"],
                    #         "picUrl": None,
                    #         "sugList": pois["type"].split(";"),
                    #         "location": pois["location"]
                    #     }
                    #     # 添加到附近
                    result["pointList"]=spots
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
    



def get_osm_tourist_spots_with_keywords(latitude, longitude, radius=5000):
    """
    查询给定经纬度坐标周边指定范围内的景点，并提取相关关键词（使用 OSM Overpass API）
    
    :param latitude: 纬度
    :param longitude: 经度
    :param radius: 搜索半径（米）
    :return: 景点列表（包含名称、坐标、关键词）
    """
    overpass_url = "https://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    (
        node["tourism"="attraction"](around:{radius},{latitude},{longitude});
        way["tourism"="attraction"](around:{radius},{latitude},{longitude});
        relation["tourism"="attraction"](around:{radius},{latitude},{longitude});
    );
    out center;
    """
    
    response = requests.get(overpass_url, params={'data': query})
    data = response.json()
    
    places = []
    for element in data.get("elements", []):
        name = element.get("tags", {}).get("name")
        if name:
            lat = element.get("lat", element.get("center", {}).get("lat"))
            lon = element.get("lon", element.get("center", {}).get("lon"))
            filtered_tags = filter_keywords(element.get("tags", {}))
            places.append({
                "location": f"{lon},{lat}",
                "picUrl": None,
                "pointName": name,
                "sugList": list(filtered_tags.keys())  # 关键词列表
            })

    return places

def filter_keywords(tags):
    """ 根据 OSM 数据筛选最相关的旅游关键词 """
    priority_keys = ["tourism", "historic", "heritage", "attraction", "castle_type", "opening_hours"]
    
    # 只保留有效的关键词
    filtered_tags = {k: v for k, v in tags.items() if k in priority_keys}
    
    # 兜底：如果筛选后为空，则至少保留 `tourism` 标签
    if not filtered_tags and "tourism" in tags:
        filtered_tags["tourism"] = tags["tourism"]

    return filtered_tags
