import requests
import re
import json
from pypinyin import lazy_pinyin
import recognize

IpAdd_url = "http://www.baidu.com/s?ie=UTF-8&wd=ip"
IpAdd = requests.get(IpAdd_url).text
IpAdd = re.findall('<span class="c-gap-right">本机IP:&nbsp;(.*?)</span>',IpAdd)[0]

AK = "KNAwUUx5Sschmz5aQNdDX4dD2er41RRL"
MapApi_url = "http://api.map.baidu.com/location/ip?ip={}&ak={}&coor=bd09ll".format(IpAdd,AK)
LocalAdd = json.loads(requests.get(MapApi_url).text)

province = lazy_pinyin(LocalAdd['content']['address_detail']['province'])
city = lazy_pinyin(LocalAdd['content']['address_detail']['city'])

province.remove('sheng')
city.remove('shi')

province = ''.join(province)
city = ''.join(city)

weather_url = "https://tianqi.moji.com/weather/china/{}/{}".format(province,city)
weather = requests.get(weather_url).text
weather_content = re.findall('<meta name="description" content="(.*?)">',weather)[0]

print(weather_content)
recognize.synthesis(weather_content)
