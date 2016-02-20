import tornado.ioloop
import tornado.web
from tornado import gen
import os
import base64
import re
import json
import numpy as np
import time
from PIL import Image

static_path = os.path.join(os.getcwd(), "static")

class Action(object):
    def __init__(self, num=None, left=False, right=False, faster=False, slower=False):
        if num is not None:
            if num > 13 or num < 0:
                raise ValueError("Invalid num, must be 0-13")
            self.left = num & (1 << 0) == (1 << 0) 
            self.right = num & (1 << 1) == (1 << 1) 
            self.faster = num & (1 << 2) == (1 << 2) 
            self.slower = num & (1 << 3) == (1 << 3) 
        else:
            self.left = left
            self.right = right
            self.faster = faster
            self.slower = slower
        if self.left and self.right:
            raise ValueError("Invalid action, cannot press both left and right")
        if self.faster and self.slower:
            raise ValueError("Invalid action, cannot press both faster and slower")

    def num(self):
        total = 0
        if self.left: total += (1 << 0)
        if self.right: total += (1 << 1)
        if self.faster: total += (1 << 2)
        if self.slower: total += (1 << 3)
        return total

    def to_dict(self):
        return {
            "keyLeft": self.left,
            "keyRight": self.right,
            "keyFaster": self.faster,
            "keySlower": self.slower
        }

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.redirect("/static/v4.final.html")

class FrameHandler(tornado.web.RequestHandler):
    def post(self, num):
        ar = np.fromstring(self.request.files["image"][0]["body"], dtype="uint8")
        height = int(self.get_arguments("height")[0])
        width = int(self.get_arguments("width")[0])
        ar = ar.reshape(height, width, 4)
        speed = float(self.get_arguments("speed")[0])
        offset = float(self.get_arguments("offset")[0])
        position = float(self.get_arguments("position")[0])
        trafficOffsets = json.loads(self.get_arguments("trafficOffsets")[0])
        trafficPositions = json.loads(self.get_arguments("trafficPositions")[0])
        # print num, speed, offset, position, trafficPositions[0], trafficOffsets[0]
        minDist = min([abs(p - position) for p in trafficPositions])
        print minDist
        # img = Image.fromarray(ar, 'RGBA')
        # img.save('test%s.png' % num)

        # informally, in lane if 0.6 <= offset <= 0.8 or offset <= 0.1
        # we might wanna double-check this

        self.write(json.dumps({
            "keyLeft": False,
            "keyRight": False,
            "keyFaster": speed < 5000,
            "keySlower": speed > 5000,
        }))


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/frame/(.*)", FrameHandler),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": static_path})
    ], debug=True)

if __name__ == "__main__":
    app = make_app()
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()