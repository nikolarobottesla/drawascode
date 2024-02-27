import cadquery as cq

from cadquery import exporters
from math import tan, pi

# dimensions in mm
# battery holder
bat_thick = 15
bat_length = 185
battery_height = 125
battery_dimensions = [bat_length, bat_thick, battery_height]
holder_wall_thickness = 5
build_max = 76
base_thickness = 10
build_height = build_max
# half_base_width / build_height = tan(pi * 15 / 180)
half_base_width = build_height * tan(pi * 16.7 / 180)
base_width = half_base_width * 2
midpoint_curve = (bat_thick / 2 + holder_wall_thickness * 2, build_max / 2)  # y,z
top_curve = (bat_thick / 2 + holder_wall_thickness, build_max)  # y,z

# battery
flat = 3
batt = cq.Workplane("YZ", origin=(0,0, base_thickness)).hLine(flat)  # workplane is offset
batt_curve_end = (bat_thick / 2, flat)
batt = batt.radiusArc(batt_curve_end, -4.7).vLine(battery_height)
batt = batt.hLine(-bat_thick / 2)
batt = batt.close()
half1 = batt.extrude(bat_length)
half2 = half1.mirror(mirrorPlane="XZ", basePointVector=(0, 0, 0))
batt = half1.union(half2)
batt = batt.translate((-bat_length / 3 ,0,0))
#del batt

# holder
holder_profile = cq.Workplane("YZ").hLine(half_base_width).vLine(base_thickness)
holder_profile = holder_profile.threePointArc(midpoint_curve, top_curve)
holder_profile = holder_profile.hLine(-holder_wall_thickness)
holder_profile = holder_profile.lineTo(bat_thick / 2 , base_thickness + flat)
holder_profile = holder_profile.radiusArc((flat, base_thickness), 4.7)
holder_profile = holder_profile.lineTo(0 , base_thickness)
holder_profile = holder_profile.close()
half1 = holder_profile.extrude(build_max)
half2 = half1.mirror(mirrorPlane="XZ", basePointVector=(0, 0, 0))
holder = half1.union(half2)
del holder_profile
del half1
del half2

# band contact
band_width = 31
band_platform = 50
centered = (False, False, False)
r = cq.Workplane("XY", origin=(0, bat_thick / 2, 0)).box(build_max, half_base_width, band_platform, centered)
holder = holder.union(r)
del r
radius = 120
sphere_y = radius + half_base_width
location = (build_max / 2, sphere_y, band_platform / 3)
sphere = cq.Workplane("XY").sphere(radius)
sphere = sphere.translate(location)
holder = holder.cut(sphere)
# del sphere
hook_width = 2
hook_depth = 3
post_dims = (12, half_base_width + 5, 10)
post1 = (0, 0)
post2 = (build_max - post_dims[0], 0)
posts = cq.Workplane("XY", origin=(0, bat_thick / 2, 0))
posts = posts.pushPoints([post1, post2])
posts = posts.box(*post_dims, centered)
# hook = cq.Workplane("XY", origin=(0, bat_thick / 2, 0))
# hook = hook.box(build_max, hook_width, hook_depth, centered)
# hook = hook.translate((0, half_base_width, post_dims[2] - hook_depth))
# posts = posts.cut(hook)
# del hook
sphere2 = sphere.translate((0, -radius, -radius - hook_depth - 4))
sphere = sphere.faces("+Z").shell(-hook_width)  # turn  sphere into shell
sphere = sphere.cut(sphere2)
posts = posts.cut(sphere)  # cut to match the bands 2nd curve
holder = holder.union(posts)
del sphere
del sphere2
del posts

# strap (s_) features
shell_thick = 2.4
s_width = 13.5
s_thick = 3.5
s_thick_s = s_thick + shell_thick * 2 # _s = with shell
s_width_s = s_width + shell_thick * 2
s_wall_thick = holder_wall_thickness - 2 * shell_thick
half_col_x = s_width / 2 + holder_wall_thickness
s_loc_x = (half_col_x, build_max / 2, build_max - half_col_x)
s_loc_y = s_thick_s + s_wall_thick + bat_thick / 2
s_locs = [(s_loc_x[0], s_loc_y), (s_loc_x[1], s_loc_y), 
          (s_loc_x[2], s_loc_y), (s_loc_x[1], -s_loc_y)]
s_holes = cq.Workplane("XY").pushPoints(s_locs)
s_holes = s_holes.rect(s_width_s, s_thick_s).extrude(build_max)
holder = holder.cut(s_holes)
del s_holes

s_col = cq.Workplane("XY", origin=(0, 0, shell_thick))
# s_col = s_col.pushPoints([(-20, 0)]) # debugging
s_col = s_col.rect(s_width_s + 2 * s_wall_thick, s_thick_s + 2 * s_wall_thick).rect(s_width_s, s_thick_s)
s_col = s_col.extrude(band_platform - 2 * shell_thick)
s_col = s_col.shell(shell_thick)

for s_loc in s_locs:
    temp = s_col.translate((*s_loc, 0))
    holder = holder.union(temp)
    del temp

del s_col

file_name = "milo_batt_holderV5.stl"
exporters.export(holder, file_name, tolerance=0.01, angularTolerance=1)