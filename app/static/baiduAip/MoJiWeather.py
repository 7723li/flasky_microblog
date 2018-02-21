import requests
import re
import json
from pypinyin import lazy_pinyin
import recognize

IpAdd_url = "http://www.baidu.com/s?ie=UTF-8&wd=ip"
IpAdd = requests.get(IpAdd_url).text
try:
    IpAdd = re.findall('<span class="c-gap-right">本机IP:&nbsp;(.*?)</span>',IpAdd)[0]
except IndexError:
    IpAdd_url = "http://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=0&rsv_idx=1&tn=baidu&wd=ip&rsv_pq=f4a0f8ad0001d798&rsv_t=c9c3O30oBtLpbzv053VsFEqMNJit%2FuxGeqYchRGt0OYCvZOfMYZyf21D7Ok&rqlang=cn&rsv_enter=1&rsv_sug3=3&rsv_sug1=1&rsv_sug7=100&rsv_sug2=0&inputT=2062&rsv_sug4=2989"
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
