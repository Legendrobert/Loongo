import requests
from bs4 import BeautifulSoup

def get_bing_image_urls(query, count=3):
    """
    使用 requests + BeautifulSoup 爬取 Bing 图片搜索结果，获取指定数量的图片 URL。

    :param query: 搜索关键词
    :param count: 获取的图片数量
    :return: 图片 URL 列表
    """
    search_url = f"https://www.bing.com/images/search?q={query}&form=HDRSC2"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    response = requests.get(search_url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    img_tags = soup.find_all("img", class_="mimg")

    # 获取图片URL
    img_urls = [img["src"] for img in img_tags if "src" in img.attrs][:count]
    return img_urls

# 测试调用
if __name__ == "__main__":
    keyword = "成都"
    urls = get_bing_image_urls(keyword)
    print(urls)