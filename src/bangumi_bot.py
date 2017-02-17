# coding=utf-8
# import requests
from lxml import html
import abc
import re
import datetime
from tornado import httpclient, gen
import json


__author__ = 'fengyuyao'


class Bot:
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.url = None

    @abc.abstractmethod
    def get_data(self):
        pass


class BilibiliBot(Bot):
    HOST = "www.bilibili.com"

    def __init__(self):
        super(BilibiliBot, self).__init__()
        # area_id 1 for China, 2 for Japan
        self.url = "http://" + self.HOST + "/api_proxy?app=bangumi&action=timeline_v2&area_id=2"
        self.name = 'Bilibili'

    @gen.coroutine
    def get_data(self):
        content = yield httpclient.AsyncHTTPClient().fetch(self.url)
        # content = requests.get(self.url)
        if not content.error:
            content = json.loads(content.body)
            if content['code'] == 0:
                content = content['list']
        else:
            raise gen.Return(None)

        # content = content[0].keys()#content[0]['title']
        bangumi_info = []

        for c in content:
            info = {}
            info['weekday'] = c['weekday']
            info['title'] = c['title']
            info['url'] = "http://" + self.HOST + c['url']
            info['updateTime'] = datetime.datetime.fromtimestamp(c['lastupdate'])
            bangumi_info.append(info)

        raise gen.Return(bangumi_info)


class TudouBot(Bot):
    HOST = "cartoon.tudou.com"
    TIME_PATTREN = re.compile(r"(\d+):(\d+).*")
    WEEKDAY = {u"周一":1,
               u"周二":2,
               u"周三":3,
               u"周四":4,
               u"周五":5,
               u"周六":6,
               u"周日":0
               }

    def __init__(self):
        super(TudouBot, self).__init__()
        # area_id 1 for China, 2 for Japan
        self.url = "http://" + self.HOST + "/api_proxy?app=bangumi&action=timeline_v2&area_id=2"
        self.name = 'Tudou'

    @gen.coroutine
    def get_data(self):
        content = yield httpclient.AsyncHTTPClient().fetch(self.url)
        # content = requests.get(self.url)
        if not content.error:
            root = html.fromstring(content.body)
        else:
            raise gen.Return(None)

        bangumi_info = []
        weekday = -1
        for e in root.xpath('//*[@id="updateSrcoll"]/li'):
            try:
                class_val = e.attrib['class'].split()
            except KeyError as err:
                if err.args[0] != 'class':
                    raise err
                else:
                    class_val = []

            if 't' in class_val:
                 weekday = self.WEEKDAY[e.xpath('i')[0].tail.strip()]
            else:
                info = {}
                info['weekday'] = weekday
                info['url'] = e.xpath('a')[0].attrib['href']
                info['title'] = e.xpath('a/i')[0].tail
                hour, minute = self.TIME_PATTREN.match(e.xpath('em')[0].text).groups()
                updateTime = datetime.time(int(hour), int(minute))
                info['updateTime'] = updateTime

                bangumi_info.append(info)

        raise gen.Return(bangumi_info)


if __name__ == '__main__':
    bbot = BilibiliBot()
    print bbot.get_data()
