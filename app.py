import base64
import csv
import hashlib
import math
import xml.etree.ElementTree as ET
from itertools import groupby

MAX_WIDTH = 1700

PROFILE_W = 40
PROFILE_H = 40
CHILD_PAD_X = 40
CHILD_PAD_Y = 40
MIN_COLS = 2
MAX_COLS = 8
FILL_COLORS = ["#dae8fc;", "#fff;"]

PROFILE_STYLE = f"shape=image;html=1;verticalAlign=top;verticalLabelPosition=bottom;labelBackgroundColor=#ffffff;imageAspect=0;aspect=fixed;image=https://cdn1.iconfinder.com/data/icons/instagram-ui-glyph/48/Sed-01-128.png;labelBackgroundColor=none;"
TEAM_STYLE = f"rounded=1;whiteSpace=wrap;html=1;verticalAlign=top;container=1;fontStyle=1;fontSize=14;"


def id(s):
    hasher = hashlib.sha1(s.encode("UTF-8"))
    return base64.urlsafe_b64encode(hasher.digest()[:10]).decode("UTF-8")


def el(root, parent, name, x, y, w, h, s=""):
    el = ET.SubElement(root, "mxCell")
    el.set("parent", parent.get("id"))
    el.set("id", id(name))
    el.set("value", name)
    el.set("vertex", "1")
    el.set("style", s)

    geom = ET.SubElement(el, "mxGeometry")
    geom.set("x", f"{x}")
    geom.set("y", f"{y}")
    geom.set("width", f"{w}")
    geom.set("height", f"{h}")
    geom.set("as", "geometry")

    return el


def run():
    mxfile = ET.Element("mxfile")
    mxfile.set("host", "app.diagrams.net")

    diagram = ET.SubElement(mxfile, "diagram")
    diagram.set("name", "Employees")
    diagram.set("id", id("Employees"))

    mx_graph_model = ET.SubElement(diagram, "mxGraphModel")
    mx_graph_model.set("id", id("mxGraphModel"))

    root = ET.SubElement(mx_graph_model, "root")
    one = ET.SubElement(root, "mxCell")
    one.set("id", "0")
    two = ET.SubElement(root, "mxCell")
    two.set("id", "1")
    two.set("parent", one.get("id"))

    with open("all.csv") as fp:
        reader = csv.reader(fp)
        data = [(y, x) for x, y in reader]

    def key_func(i):
        k, _ = i
        return k

    tx, ty = 40, 40
    # max height of the current row
    th_max = 0
    # current business unit
    t_bu = ""
    # current fill color
    fill_i = 0

    grouped_data = groupby(sorted(data, key=key_func), key=key_func)
    for group, v in grouped_data:

        # "newline logic", split beyond max_width or if it's a new team
        if tx > MAX_WIDTH or group.split(" ")[0] != t_bu:
            tx = 40
            ty = ty + th_max + 40
            th_max = 0
            fill_i = 1 if fill_i == 0 else 0

        v = list(v)

        cols, tw, th = team_dim(len(v))
        th_max = max(th_max, th)
        t_bu = group.split(" ")[0]
        t_el = el(root, two, group, x=tx, y=ty, w=tw, h=th, s=TEAM_STYLE + f"fillColor={FILL_COLORS[fill_i]}")

        for i, item in enumerate(v):
            _, name = item

            x_i = (i % cols)
            y_i = math.floor(i / cols)
            x = x_i * PROFILE_W + x_i * CHILD_PAD_X * 2 + CHILD_PAD_X
            y = y_i * PROFILE_H + y_i * CHILD_PAD_Y * 2 + CHILD_PAD_Y
            el(root, t_el, name, x=x, y=y, w=40, h=40, s=PROFILE_STYLE)

        tx = tx + tw
        ty = ty

    with open("all.xml", "wb") as fp:
        fp.write(ET.tostring(mxfile))


def team_dim(n, child_w=PROFILE_W, child_h=PROFILE_H, pad_x=10, pad_y=10, ):
    cols = max(MIN_COLS, min(n, MAX_COLS))
    i_y = math.ceil(n / MAX_COLS)
    return [cols,
            cols * child_w + cols * CHILD_PAD_X * 2 + pad_x * 2,
            i_y * child_h + i_y * CHILD_PAD_Y * 2 + pad_y * 2]


if __name__ == "__main__":
    run()
