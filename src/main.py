import tornado.ioloop
import tornado.web
from tornado import gen
import bangumi_bot
import difflib
import datetime
import time

__author__ = 'fengyuyao'


class MainHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        print 1
        res = yield self.get_data()

        # print res
        # self.write(str(res))
        cur_date = datetime.datetime.now()
        self.render("../templates/index.html", bangumi_info=res, cur_weekday=cur_date.weekday())

    @gen.coroutine
    def get_data(self):
        bangumi_info = {}

        for i in range(7):
            bangumi_info['day%d' % i] = []
        bangumi_info['day%d' % -1] = []

        bots = [bangumi_bot.TudouBot(), bangumi_bot.BilibiliBot()]
        for bot in bots:
            data = yield bot.get_data()
            for cur_record in data:
                info_in_day = bangumi_info['day%d' % cur_record['weekday']]

                for iRecord in info_in_day:
                    if self._bangumi_similar(iRecord, cur_record) > 0.5:
                        iRecord['url'][bot.name] = (cur_record['url'])
                        break
                else:
                    cur_record['url'] = {bot.name: cur_record['url']}
                    info_in_day.append(cur_record)

        raise gen.Return(bangumi_info)

    def _bangumi_similar(self, a, b):
         return difflib.SequenceMatcher(a=a['title'], b=b['title']).ratio()


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
