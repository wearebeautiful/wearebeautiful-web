#!/usr/bin/env python3

import sys
import colorsys
from math import fmod
import config

template = """@import "node_modules/bootstrap/scss/bootstrap";

$theme-colors: (
    "primary":   #%s,  // used for history pills
    "secondary": #%s,  // used for tags pills
    "info":      #%s,  // related info to model pills
    "light":     #%s,  // backgrounds and such 
    "danger":    #%s   // danger
);

$link-color:       #%s;
$link-hover-color: #%s;
$link-visited-color: #%s;

@import "bootstrap";
"""

def tweak_hue(rgb, tweak):
    h, s, v = colorsys.rgb_to_hsv(rgb[0] / 255.0, rgb[1] / 255.0, rgb[2]/ 255.0)
    h += tweak
    if h > 1.0:
        h = fmod(h, 1.0)
    if h < 0.0:
        h += 1.0
    temp = colorsys.hsv_to_rgb(h, s, v)
    return "%02X%02X%02X" % (int(temp[0] * 255), int(temp[1] * 255), int(temp[2] * 255)) 

def tweak_value(rgb, tweak):
    h, s, v = colorsys.rgb_to_hsv(rgb[0] / 255.0, rgb[1] / 255.0, rgb[2]/ 255.0)

    v += tweak
    if v > 1.0:
        v = fmod(v, 1.0)
    if v < 0.0:
        v += 1.0

    temp = colorsys.hsv_to_rgb(h, s, v)
    return "%02X%02X%02X" % (int(temp[0] * 255), int(temp[1] * 255), int(temp[2] * 255)) 


base_col = config.THEME_BASE_COLOR
rgb = tuple(int(base_col[i:i+2], 16) for i in (0, 2, 4))

comp_col_0 = tweak_hue(rgb, -.03)
comp_col_1 = tweak_hue(rgb, -.06)
hover_col = tweak_value(rgb, .15)
visited_col = tweak_value(rgb, -.15)
danger = tweak_hue(rgb, -.045)



with open("static/scss/custom.scss", "w") as f:
    f.write(template % (
        config.THEME_BASE_COLOR,
        comp_col_0,
        comp_col_1,
        config.BG_COLOR,
        danger, 
        base_col,
        hover_col,
        visited_col))
