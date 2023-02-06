#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2023/1/31

import asyncio
import json

import tornado.web


class MainHandler(tornado.web.RequestHandler):

    def get(self):
        self.write("hello world")


class TestApiHandler(tornado.web.RequestHandler):

    def get(self):
        data = [{"value": 1, "label": "james"}, {"value": 2, "label": "zhang"},
                {"value": 3, "label": "peng"}]
        self.write(json.dumps(data))


def make_app():
    return tornado.web.Application(
        [
            (r"/", MainHandler),
            (r"/testApi", TestApiHandler)
        ]
    )


async def star_service(port: int):
    app = make_app()
    app.listen(port)
    await asyncio.Event().wait()


if __name__ == '__main__':
    asyncio.run(star_service(9999))
