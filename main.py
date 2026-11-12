import math

import cairo

from src import tilings
from src import geometry_types as gt

X_GRID_RANGE = 10
Y_GRID_RANGE = 10
ZOOM_OUT = 2

VIEW_X_GRID_RANGE = 1000
VIEW_Y_GRID_RANGE = 1000

# Star pattern parameters
# TODO: Make this command line arguments
CONTACT_ANGLE = math.radians(50)
DELTA = 0.0
STEP = 2


# Most of this code is borrowed from a side
# project, which I decided to turn into my
# final project.
def get_ray_intersection(ray1: gt.Ray, ray2: gt.Ray) -> tuple[float, float] | None:
    if ray1.origin == ray2.origin:
        return

    d = ray2.origin - ray1.origin
    det = ray1.direction.cross(ray2.direction)

    if det == 0:
        return None

    u = d.cross(ray2.direction) / det
    v = d.cross(ray1.direction) / det

    if u <= 1e-9 or v <= 1e-9:
        return
    return u, v

def kaplan_star_generator(polygon: gt.Polygon) -> list[gt.Segment]:
    n = len(polygon.segments)
    rays: list[gt.Ray] = []
    for i in range(n):
        segment = polygon.segments[i]

        midpoint = segment.midpoint()
        edge_dir = (segment.end - segment.start).normalize()
        inward_normal = gt.Vector2(-edge_dir.y, edge_dir.x)

        origin_a = midpoint - (edge_dir * DELTA)
        origin_b = midpoint + (edge_dir * DELTA)

        direction_a = (edge_dir * math.cos(CONTACT_ANGLE)) + (inward_normal * math.sin(CONTACT_ANGLE))
        direction_b = (edge_dir * -math.cos(CONTACT_ANGLE)) + (inward_normal * math.sin(CONTACT_ANGLE))

        rays.append(gt.Ray(origin_a, direction_a))
        rays.append(gt.Ray(origin_b, direction_b))

    intersections_and_costs: list[tuple[gt.Ray, gt.Ray, gt.Vector2, float]] = []
    for ray1 in rays:
        for ray2 in rays:
            if ray1 != ray2 and ray1.origin != ray2.origin:
                res = get_ray_intersection(ray1, ray2)
                if not res:
                    continue
                u, v = res
                cost = u + v
                point = ray1.origin + ray1.direction * u
                intersections_and_costs.append((ray1, ray2, point, cost))

    intersections_and_costs.sort(key=lambda x: x[3])
    star_segments: list[gt.Segment] = []
    encountered_rays: dict[gt.Ray, int] = {}
    for ray1, ray2, point, cost in intersections_and_costs:
        ray1_encounters = encountered_rays.get(ray1, 0)
        ray2_encounters = encountered_rays.get(ray2, 0)
        if ray1_encounters == STEP or ray2_encounters == STEP:
            continue

        ray1_encounters += 1
        ray2_encounters += 1

        ray1_segment = gt.Segment(ray1.origin, point)
        ray2_segment = gt.Segment(ray2.origin, point)
        star_segments.append(ray1_segment)
        star_segments.append(ray2_segment)

        encountered_rays[ray1] = ray1_encounters
        encountered_rays[ray2] = ray2_encounters

    return star_segments

def main():
    tiling = tilings.regular_square_tiling(X_GRID_RANGE, Y_GRID_RANGE)

    star_segments: list[gt.Segment] = []
    for tile in tiling.tiles:
        star_segments += kaplan_star_generator(tile)

    x_scale_factor, y_scale_factor = VIEW_X_GRID_RANGE / X_GRID_RANGE, VIEW_Y_GRID_RANGE / Y_GRID_RANGE
    with cairo.SVGSurface("output.svg", VIEW_X_GRID_RANGE, VIEW_Y_GRID_RANGE) as surface:
        context = cairo.Context(surface)
        context.set_source_rgb(0, 0, 0)
        for segment in star_segments:
            context.set_line_width(0.5)

            # We have to flip the Y-coordinates for SVG
            start_x = segment.start.x * x_scale_factor
            start_y = VIEW_Y_GRID_RANGE - (segment.start.y * y_scale_factor)
            end_x = segment.end.x * x_scale_factor
            end_y = VIEW_Y_GRID_RANGE - (segment.end.y * y_scale_factor)

            context.move_to(start_x, start_y)
            context.line_to(end_x, end_y)
            context.stroke()

if __name__ == "__main__":
    main()
