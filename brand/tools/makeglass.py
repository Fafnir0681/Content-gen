#!/usr/bin/env python3
"""Regenerate the glass overlay variants from brand/mark/mark-full.svg.
The glass is a clipped overlay; the mark geometry underneath is untouched.
Disc centre (1024,1024), r=428 in a 2048 viewBox.
Animate <linearGradient id="sheen"> x1/y1/x2/y2 to sweep light across the disc.
Usage: python3 tools/makeglass.py
"""
import os, re
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(HERE, 'mark', 'mark-full.svg')).read()
body = src[src.index('>', src.index('<svg')) + 1:].replace('</svg>', '')
HEAD = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2048 2048" width="2048" height="2048">'
CX = CY = 1024; R = 428

def morph(film, sheen, rim_o, rim_w):
    return (f'<defs><clipPath id="disc"><circle cx="{CX}" cy="{CY}" r="{R}"/></clipPath>'
      f'<linearGradient id="sheen" x1="0.05" y1="0" x2="0.75" y2="1">'
      f'<stop offset="0%" stop-color="#fff" stop-opacity="{sheen}"/>'
      f'<stop offset="42%" stop-color="#fff" stop-opacity="{sheen*0.35:.3f}"/>'
      f'<stop offset="43%" stop-color="#fff" stop-opacity="0"/>'
      f'<stop offset="100%" stop-color="#fff" stop-opacity="0"/></linearGradient>'
      f'<linearGradient id="rimg" x1="0.15" y1="0" x2="0.85" y2="1">'
      f'<stop offset="0%" stop-color="#fff" stop-opacity="{rim_o}"/>'
      f'<stop offset="40%" stop-color="#fff" stop-opacity="{rim_o*0.25:.3f}"/>'
      f'<stop offset="72%" stop-color="#fff" stop-opacity="{rim_o*0.55:.3f}"/>'
      f'<stop offset="100%" stop-color="#fff" stop-opacity="{rim_o*0.9:.3f}"/></linearGradient></defs>'
      + body
      + f'<g clip-path="url(#disc)"><circle cx="{CX}" cy="{CY}" r="{R}" fill="#fff" fill-opacity="{film}"/>'
      f'<circle cx="{CX}" cy="{CY}" r="{R}" fill="url(#sheen)"/>'
      f'<circle cx="{CX}" cy="{CY}" r="{R-rim_w/2}" fill="none" stroke="url(#rimg)" stroke-width="{rim_w}"/></g>')

def dome(g0, g1, e1, e2, b0, r0, r1, gr, rw, x1, y1, x2, y2):
    return (f'<defs><clipPath id="disc"><circle cx="{CX}" cy="{CY}" r="{R}"/></clipPath>'
      f'<linearGradient id="sheen" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">'
      f'<stop offset="0%" stop-color="#fff" stop-opacity="{g0}"/>'
      f'<stop offset="55%" stop-color="#fff" stop-opacity="{g1}"/>'
      f'<stop offset="100%" stop-color="#fff" stop-opacity="0"/></linearGradient>'
      f'<radialGradient id="edge" cx="50%" cy="50%" r="50%">'
      f'<stop offset="58%" stop-color="#000" stop-opacity="0"/>'
      f'<stop offset="86%" stop-color="#000" stop-opacity="{e1}"/>'
      f'<stop offset="100%" stop-color="#000" stop-opacity="{e2}"/></radialGradient>'
      f'<radialGradient id="bounce" cx="50%" cy="50%" r="50%">'
      f'<stop offset="0%" stop-color="#fff" stop-opacity="{b0}"/>'
      f'<stop offset="100%" stop-color="#fff" stop-opacity="0"/></radialGradient>'
      f'<linearGradient id="rim" x1="0" y1="0" x2="0" y2="1">'
      f'<stop offset="0%" stop-color="#fff" stop-opacity="{r0}"/>'
      f'<stop offset="45%" stop-color="#fff" stop-opacity="0.04"/>'
      f'<stop offset="100%" stop-color="#fff" stop-opacity="{r1}"/></linearGradient></defs>'
      + body
      + f'<g clip-path="url(#disc)">'
      f'<ellipse cx="{CX}" cy="{int(CY-R*0.40)}" rx="{int(R*0.82)}" ry="{int(R*gr)}" fill="url(#sheen)"/>'
      f'<ellipse cx="{CX}" cy="{int(CY+R*0.60)}" rx="{int(R*0.60)}" ry="{int(R*0.28)}" fill="url(#bounce)"/>'
      f'<circle cx="{CX}" cy="{CY}" r="{R}" fill="url(#edge)"/>'
      f'<circle cx="{CX}" cy="{CY}" r="{R-rw/2}" fill="none" stroke="url(#rim)" stroke-width="{rw}"/></g>')

VARIANTS = {
 'morph-clean.svg':   morph(0.07, 0.26, 0.55, 7),
 'morph-streak.svg':  morph(0.10, 0.32, 0.70, 9),
 'morph-frosted.svg': morph(0.14, 0.40, 0.85, 11),
 'lens-edge.svg':     dome(0.0, 0.0, 0.14, 0.46, 0.10, 0.95, 0.55, 0.01, 13, 0, 0, 0, 1),
 'dome-subtle.svg':   dome(0.30, 0.05, 0.10, 0.26, 0.08, 0.70, 0.26, 0.44, 6, 0, 0, 0, 1),
 'tile-diagonal.svg': dome(0.52, 0.34, 0.16, 0.38, 0.14, 0.90, 0.34, 0.52, 10, 0.08, 0, 0.80, 1),
}
for name, inner in VARIANTS.items():
    open(os.path.join(HERE, 'glass-motion', name), 'w').write(HEAD + inner + '</svg>')
    print('wrote', name)
