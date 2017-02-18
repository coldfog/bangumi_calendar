# coding=utf-8
import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado import gen
import bangumi_bot
import difflib
import datetime
import os
from tornado.options import define, options
import json
import logging

__author__ = 'fengyuyao'

define("port", default=8888, help="run on the given port", type=int)
# define("logging", default="info",
#        help=("Set the Python log level. If 'none', tornado won't touch the "
#              "logging configuration."),
#        metavar="debug|info|warning|error|none")

WEEKDAY_NAME = [u"星期日", u"星期一", u"星期二", u"星期三", u"星期四", u"星期五", u"星期六"]


class MainHandler(tornado.web.RequestHandler):
    # @gen.coroutine
    def get(self):
        cur_weekday = datetime.datetime.now().weekday() + 1
        # for Sunday, in database Sunday is 0
        if cur_weekday == 7:
            cur_weekday = 0
        self.render("../templates/index.html",
                    bangumi_info=self.application.bangumi_info,
                    cur_weekday=cur_weekday,
                    WEEKDAY_NAME=WEEKDAY_NAME)


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.time):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)


class RawJsonHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(self.application.bangumi_info_json)


class Application(tornado.web.Application):
    def __init__(self):
        settings = {
            "static_path": os.path.join(os.path.dirname(__file__), '..', "static"),
            "debug": True
        }

        handler = [
            (r"/", MainHandler),
            (r"/raw_json", RawJsonHandler),
            (r"/(.*)", tornado.web.StaticFileHandler,
             dict(path=settings['static_path'])),
        ]
        super(Application, self).__init__(handler, **settings)

        self.bangumi_info = {}
        self.bangumi_info_json = ''
        tornado.ioloop.IOLoop.current().run_sync(self.update_bangumi_infor)
        # everyday update one time
        self.get_data_task = tornado.ioloop.PeriodicCallback(self.update_bangumi_infor, 1000 * 60 * 60 * 24)
        self.get_data_task.start()

    @gen.coroutine
    def update_bangumi_infor(self):
        logging.info("Start to update bangumi_info")
        bangumi_info = {}
        for i in range(7):
            bangumi_info[i] = []
        bangumi_info[-1] = []

        bots = [bangumi_bot.TudouBot(), bangumi_bot.BilibiliBot(), bangumi_bot.YoukuBot(), bangumi_bot.IQiyiBot()]
        for bot in bots:
            data = yield bot.get_data()
            for cur_record in data:
                info_in_day = bangumi_info[cur_record['weekday']]

                for iRecord in info_in_day:
                    if self._bangumi_similar(iRecord, cur_record) > 0.5:
                        iRecord['url'][bot.name] = cur_record['url']
                        iRecord['update_time'][bot.name] = cur_record['update_time']
                        break
                else:
                    cur_record['url'] = {bot.name: cur_record['url']}
                    cur_record['update_time'] = {bot.name: cur_record['update_time']}
                    info_in_day.append(cur_record)

        def _cmp(x, y):
            x_utime = x['update_time']
            y_utime = y['update_time']

            # only use not None val
            for k in x_utime:
                if x_utime[k]:
                    x_utime = x_utime[k]
                    break
            else:
                return 1

            for k in y_utime:
                if y_utime[k]:
                    y_utime = y_utime[k]
                    break
            else:
                return 1

            if x_utime > y_utime:
                return 1
            elif x_utime < y_utime:
                return -1
            else:
                return 0

        for key in bangumi_info:
            bangumi_info[key].sort(cmp=_cmp)

        self.bangumi_info = bangumi_info
        enconder = DateTimeEncoder()
        self.bangumi_info_json = enconder.encode(self.bangumi_info)
        logging.info("finish updating bangumi_info")

    @staticmethod
    def _bangumi_similar(a, b):
        return difflib.SequenceMatcher(a=a['title'], b=b['title']).ratio()


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
