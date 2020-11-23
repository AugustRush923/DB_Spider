import re
import time
import json
import random
import requests

from utils import write_header, write2csv, csv2xlsx


class DNBSpider:
    def __init__(self, cookie=None, query=None):
        self.url = "https://hoovers.mmdnb.com/api/search"
        self.user_agent = [
            "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
            "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
            "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0",
            "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.3; rv:11.0) like Gecko",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",
            "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
            "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
            "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11",
            "Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36 Edg/86.0.622.58"]
        self.headers = {
            "Cookie": cookie,
            "User-Agent": random.choice(self.user_agent),
            "Content-Type": "application/json",
        }
        self.payload = {
            "query": query,
            "searchWeight": 0,
            "filters": [],
            "aggs": {},
            "from": 0,
            "size": 25,
            "sortBy": [],
            "types": ["company"]
        }
        self.proxies = [
            {
                "http": "1.198.72.20:9999",
                "https": "177.73.170.165:8080"
            },
            {
                "http": "62.91.90.130:8080",
                "https": "36.248.129.42:9999"
            },
            {
                "http": "125.160.196.176:3128",
                "https": "186.226.185.82:6666"
            }]
        self.fieldnames = ['id', 'companyName', 'primaryUrl', 'phone', 'country0', 'state0', 'city0', 'address0',
                           'country1', 'state1', 'city1', 'address1', 'address-0', 'address-1', 'companyType',
                           'industry']

    def request_target(self, url, data):
        payload_data = json.dumps(data)
        response = requests.post(url=url, headers=self.headers, data=payload_data, proxiex=random.choice(self.proxies))
        if response.status_code == 200:
            return json.loads(response.text)
        if response.status_code == 400:
            raise Exception('最大获取深度。')
        if response.status_code == 404:
            raise TypeError('Cookie过期，请更换Cookie再试。')

    def parse_data(self, data):
        results = data['searchResults']['results']
        for result in results:
            item = dict()
            item['id'] = result['id']
            item['companyName'] = result['companyName']
            item['primaryUrl'] = result['primaryUrl']
            item['phone'] = result['phone']
            for i in range(len(result['addresses'])):
                if result['addresses'][i].get('country').get('name') is None:
                    item[f'country{i}'] = ''
                else:
                    item[f'country{i}'] = result['addresses'][i].get('country').get('name')

                if result['addresses'][i].get('state').get('name') is None:
                    item[f'state{i}'] = ''
                else:
                    item[f'state{i}'] = result['addresses'][i].get('state').get('name')

                if result['addresses'][i].get('city') is None:
                    item[f'city{i}'] = ''
                else:
                    item[f'city{i}'] = result['addresses'][i].get('city')

                if result['addresses'][i].get('address1') is None:
                    item[f'address{i}'] = ''
                else:
                    item[f'address{i}'] = result['addresses'][i].get('address1')
                item[f'address-{i}'] = item[f'country{i}'] + ' ' + item[f'state{i}'] + ' ' + item[f'city{i}'] + ' ' + \
                    item[f'address{i}']
            item['companyType'] = result['ownershipType'].get('name') + ' ' + result['entityType'].get('name')
            item['industry'] = result['industry'].get('shortDescription')
            print(item)
            write2csv(self.payload.get('query'), item, fieldnames=self.fieldnames)

    def get_user_id(self, logon_id):
        get_userid_url = "https://hoovers.mmdnb.com/api/auth/login-details"
        get_userid_payload = {
            "username": logon_id
        }
        result = self.request_target(get_userid_url, get_userid_payload)
        user_id = result.get('UserID')
        return user_id

    def login(self, username, password):
        login_url = "https://hoovers.mmdnb.com/api/auth/login"
        user_id = self.get_user_id(username)
        login_payload = {
            "logonId": user_id,
            "password": password
        }
        response = requests.post(url=login_url, headers=self.headers, data=json.dumps(login_payload))
        cookie = response.headers.get('Set-Cookie')
        jessionid = re.findall(r'JSESSIONID=.*?;', cookie)[0]
        ext_id = re.findall(r'ext_id=.*?;', cookie)[0]
        print(f'当前ext_id为{ext_id}, 当前jessionid为{jessionid}')
        self.headers['Cookie'] = jessionid + ext_id

    def runserver(self):
        write_header(self.payload.get('query'), fieldnames=self.fieldnames)
        res = self.request_target(self.url, self.payload)
        total_count = res['searchResults']['totalCount']
        total_page = total_count / 25 if total_count % 25 == 0 else total_count // 25 + 1

        print(f'*****共{total_page}页*****')
        print('-' * 20)

        for page_num in range(total_page):
            time_list = [2, 3, 4, 5]
            time.sleep(random.choice(time_list))
            self.parse_data(self.request_target(self.url, self.payload))
            self.payload['from'] += 25
            self.headers['HPK'] = str(round(time.time() * 1000)) + '-' + str(self.payload['from'])
            print(f'当前第{page_num + 1}页')
            print(self.payload['from'])
            print('*' * 20)
        csv2xlsx(self.payload.get('query'))


if __name__ == '__main__':
    query_item = input("请输入要查询的关键字:")
    spider = DNBSpider(query=query_item)
    try:
        spider.runserver()
    except TypeError:
        spider.login(username='username', password='password')
        spider.runserver()
