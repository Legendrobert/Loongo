import requests
import math

#搜厕所


def filter_keywords(tags):
    """ 根据 OSM 数据筛选最相关的厕所关键词 """
    priority_keys = ["amenity"]
    
    # 只保留有效的关键词
    filtered_tags = {k: v for k, v in tags.items() if k in priority_keys}
    
    # 兜底：如果筛选后为空，则至少保留 `amenity` 标签
    if not filtered_tags and "amenity" in tags:
        filtered_tags["amenity"] = tags["amenity"]

    return filtered_tags

def calculate_distance(lat1, lon1, lat2, lon2):
    """ 计算两点之间的地理距离（单位：米） """
    R = 6371000  # 地球半径（米）
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def get_nearest_toilets(latitude, longitude, radius=5000):
    """ 查询并筛选最近的厕所，并按距离排序 """
    overpass_url = "https://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    (
        node["amenity"="toilets"](around:{radius},{latitude},{longitude});
        way["amenity"="toilets"](around:{radius},{latitude},{longitude});
        relation["amenity"="toilets"](around:{radius},{latitude},{longitude});
    );
    out center;
    """
    
    response = requests.get(overpass_url, params={'data': query})
    data = response.json()
    
    toilets = []
    for element in data.get("elements", []):
        name = element.get("tags", {}).get("name", "公共厕所")
        lat = element.get("lat", element.get("center", {}).get("lat"))
        lon = element.get("lon", element.get("center", {}).get("lon"))
        filtered_tags = filter_keywords(element.get("tags", {}))
        distance = calculate_distance(latitude, longitude, lat, lon)
        toilets.append({
            "location": f"{lon},{lat}",
            "picUrl": None,
            "pointName": name,
            "sugList": list(filtered_tags.values()),  # 关键词列表
            "distance": distance  # 距离（米）
        })
    
    # 按距离排序
    toilets.sort(key=lambda x: x["distance"])
    return toilets

if __name__ == "__main__":
    latitude = 39.9042
    longitude = 116.4074
    toilets = get_nearest_toilets(latitude, longitude)
    
    for toilet in toilets:
        print(toilet)
