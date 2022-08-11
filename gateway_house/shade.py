import math

import cadquery as cq
import numpy as np

from cadquery import exporters

# dimensions are in inches

platform_thickness = 7 / 8
material_thickness = 5 / 32
half_thick = material_thickness / 2
side_bot = 11
side_back = 21
side_front = 16
side_top = math.hypot(side_bot, (side_back - side_front))
front_height = side_front - material_thickness
front_width = 12
top_width = front_width
top_angle = math.atan((side_back - side_front) / side_bot) * 180 / math.pi

hook_length = .7
hook_width = .25
hook_width2 = .35
hook_opening = material_thickness
bot_hook_open = platform_thickness
n_bot_hooks = 4
n_front_hooks = 5
hook_edge_offset = 1

tripple_false = (False, False, False)
side = cq.Workplane("XY").lineTo(side_bot, 0).lineTo(side_bot, side_front)
side = side.lineTo(0, side_back).close().extrude(material_thickness)


def repeat_hooks(hook, n_hooks, length, direction):
    hooks = cq.Workplane("XY")
    for i in range(n_hooks):
        distance = (i + 0.5) * length / n_hooks
        trans = direction * distance
        temp = hook.translate(list(trans))
        hooks = hooks.union(temp)
    del temp

    return hooks


# bottom hooks, probably will use screws instead
# hook = cq.Workplane("XY").lineTo(hook_length, 0).lineTo(hook_length, -hook_width - bot_hook_open)
# hook = hook.lineTo(0, -hook_width - bot_hook_open).lineTo(0, -bot_hook_open)
# hook = hook.lineTo(hook_length - hook_width2, -bot_hook_open).lineTo(hook_length - hook_width2, 0)
# hook = hook.close().extrude(material_thickness)
#
# hooks = repeat_hooks(hook, n_bot_hooks, side_bot, np.array((1, 0, 0)))
# side = side.union(hooks)

# front and top hook template
hook = cq.Workplane("XY").lineTo(hook_length, 0).lineTo(hook_length, -hook_width - hook_opening)
hook = hook.lineTo(0, -hook_width - hook_opening).lineTo(0, -hook_opening)
hook = hook.lineTo(hook_length - hook_width2, -hook_opening).lineTo(hook_length - hook_width2, 0)
hook = hook.close().extrude(material_thickness)

# front hooks
front_hook = hook.rotate((0, 0, 0), (0, 0, 1), (90)).translate((side_bot, 0, 0))
front_hook = front_hook.rotate((0, 0, half_thick), (1, 0, half_thick), (180))
hooks = repeat_hooks(front_hook, n_front_hooks, side_front, np.array((0, 1, 0)))
side = side.union(hooks)
del front_hook

# top hooks
top_hook = hook.rotate((0, 0, half_thick), (1, 0, half_thick), (180))
top_hook = top_hook.translate((side_bot, side_front, 0))
hooks = repeat_hooks(top_hook, n_bot_hooks, side_top, np.array((-1, 0, 0)))
hooks = hooks.rotate((side_bot, side_front, 0), (side_bot, side_front, 1), -top_angle)
side = side.union(hooks)
del top_hook

del hook, hooks

side = side.rotate((0, 0, 0), (1, 0, 0), 90)
side2 = side.translate((0, front_width, 0))
side = side.translate((0, material_thickness, 0))
sides = side.union(side2)
del side, side2

# front
front_origin = (side_bot + hook_opening, -hook_width2, hook_width2)
front = cq.Workplane("XY", origin=front_origin)
front = front.box(material_thickness, front_width + 2 * hook_width2, front_height, centered=tripple_false)
front = front.cut(sides)
front = front.translate((-material_thickness, 0, -hook_width2))

# top
top_origin = (side_bot + hook_opening, -hook_width2, side_front + hook_width2 - 0.5)
top = cq.Workplane("XY", origin=top_origin)
top = top.box(material_thickness, front_width + 2 * hook_width2, side_top + 1, centered=tripple_false)
top = top.rotate((side_bot, 0, side_front), (side_bot, 1, side_front), -90 + top_angle)
top = top.cut(sides)
top = top.rotate((side_bot, 0, side_front), (side_bot, 1, side_front), 90 - top_angle)
top = top.translate((-material_thickness, 0, -hook_width2))
top_surface = top
top = top.rotate((side_bot, 0, side_front), (side_bot, 1, side_front), -90 + top_angle)

# export dxfs for lasering

side_surface = sides.faces(">Y").workplane().section()
exporters.export(side_surface, 'side.dxf')

bnd_bx = cq.Workplane("XY").box(1, front_width + 2 * hook_width2 + 1, side_front + side_top + 1, centered=tripple_false)
bnd_bx = bnd_bx.translate((-0.5,-0.5,-0.5))

front_surface = front.union(bnd_bx)
front_surface = front_surface.faces(">X").workplane().section()
exporters.export(front_surface, 'front.dxf')

top_surface = top_surface.faces(">X").workplane().section()
exporters.export(top_surface, 'top.dxf')
