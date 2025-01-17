# -*- coding: utf-8 -*-
"""Color calculations.
"""
import colorsys

# noinspection PyAugmentAssignment
# import hashlib


def frange(start, end, step):
    """Like range(), but with floats.
    """
    val = start
    while val < end:
        yield val
        val += step


def distinct_hues(count):
    """Return ``count`` hues, equidistantly spaced.
    """
    for i in frange(0., 360., 360. / count):
        yield i / 360.


class ColorSpace(object):
    def __init__(self, nodes):
        self.nodes = {}
        for node in nodes:
            # print 'xx', node.name, node.bacon
            parts = node.name.split('.')
            self.add_to_tree(parts, self.nodes)
        self.basecolors = distinct_hues(len(self.nodes))
        self.colors = dict(zip(sorted(self.nodes.keys()), self.basecolors))

    def add_to_tree(self, parts, tree):
        if not parts:
            return
        first, rest = parts[0], parts[1:]
        if first not in tree:
            tree[first] = {}
        self.add_to_tree(rest, tree[first])

    def color(self, src):
        nodename = src.name
        parts = nodename.split('.')
        hue = self.colors[parts[0]]
        saturation = min(0.95, 0.4 + 0.1 * (src.out_degree - 1))
        lightness = max(0.3, 0.5 - 0.02 * (src.in_degree - 1))
        # lightness = 0.4
        # print "src: %s H=%s S=%s L=%s, in=%d, out=%d" % (
        #  src.name, hue, saturation, lightness, src.in_degree, src.out_degree)
        bg = rgb2eightbit(colorsys.hls_to_rgb(hue, lightness, saturation))
        black = (0, 0, 0)
        white = (255, 255, 255)
        fg = foreground(bg, black, white)
        return bg, fg

    def __str__(self):  # pragma: nocover
        import pprint
        return pprint.pformat(self.colors)


def rgb2eightbit(rgb):
    """Convert floats in [0..1] to integers in [0..256)
    """
    return tuple(int(x * 256) for x in rgb)


def name2rgb(hue):
    """Originally used to calculate color based on module name.
    """
    r, g, b = colorsys.hsv_to_rgb(hue / 360.0, .8, .7)
    return tuple(int(x * 256) for x in [r, g, b])


def brightness(r, g, b):
    """From w3c (range 0..255).
    """
    return (r * 299 + g * 587 + b * 114) / 1000


def brightnessdiff(a, b):
    """greater than 125 is good.
    """
    return abs(brightness(*a) - brightness(*b))


def colordiff(rgb1, rgb2):
    """From w3c (greater than 500 is good).
       (range [0..765])
    """
    (r, g, b) = rgb1
    (r2, g2, b2) = rgb2
    return (
        max(r, r2) - min(r, r2) +
        max(g, g2) - min(g, g2) +
        max(b, b2) - min(b, b2)
    )


def foreground(background, *options):
    """Find the best foreground color from `options` based on `background`
       color.
    """
    def absdiff(a, b):
        return brightnessdiff(a, b)
        # return 3 * brightnessdiff(a, b) + colordiff(a, b)
    diffs = [(absdiff(background, color), color) for color in options]
    diffs.sort(reverse=True)
    return diffs[0][1]


def rgb2css(rgb):
    """Convert rgb to hex.
    """
    return '#%02x%02x%02x' % rgb
