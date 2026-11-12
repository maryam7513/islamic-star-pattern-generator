import math

import cairo

from src import tilings
from src import geometry_types as gt

X_GRID_RANGE = 1
Y_GRID_RANGE = 1
ZOOM_OUT = 2

VIEW_X_GRID_RANGE = 1000
VIEW_Y_GRID_RANGE = 1000

# Star pattern parameters
# TODO: Make this command line arguments
CONTACT_ANGLE = math.radians(50)
DELTA = 0.0
STEP = 1


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

def kaplan_star_generator(polygon: gt.Polygon) -> tuple[list[gt.Ray], list[gt.Segment]]:
    n = len(polygon.segments)
    rays: list[gt.Ray] = []
    for i in range(n):
        segment = polygon.segments[i]
        midpoint = segment.midpoint()

        edge_dir = (segment.end - segment.start).normalize()
        origin_a = midpoint - (edge_dir * DELTA)
        origin_b = midpoint + (edge_dir * DELTA)

        # Use the slope of the line
        # perpendicular to the segment
        # as the basis for the normal.
        change_x, change_y = edge_dir.x, edge_dir.y
        if change_y == 0:
            perpendicular_slope = 1
        else:
            perpendicular_slope = -(change_x/change_y)

        target_point = gt.Vector2(midpoint.x + 0.25, perpendicular_slope*(midpoint.x + 0.25) + midpoint.y)
        if not polygon.in_bounds(target_point):
            target_point = gt.Vector2(midpoint.x - 0.25, perpendicular_slope*(midpoint.x - 0.25) + midpoint.y)
        inward_normal = (target_point - midpoint).normalize()

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

                if not polygon.in_bounds(point):
                    continue

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

    return rays, star_segments

def main():
    tiling = tilings.regular_square_tiling(X_GRID_RANGE, Y_GRID_RANGE)

    rays: list[gt.Ray] = []
    star_segments: list[gt.Segment] = []
    for tile in tiling.tiles:
        new_rays, new_segments = kaplan_star_generator(tile)
        rays += new_rays
        star_segments += new_segments

    print(tiling.tiles)
    print(len(rays))

    x_scale_factor, y_scale_factor = VIEW_X_GRID_RANGE / X_GRID_RANGE, VIEW_Y_GRID_RANGE / Y_GRID_RANGE
    with cairo.SVGSurface("output.svg", VIEW_X_GRID_RANGE, VIEW_Y_GRID_RANGE) as surface:
        context = cairo.Context(surface)
        context.set_line_width(0.5)

        # Debug, see source tilings
        RED = (1, 0, 0)
        BLUE = (0, 0, 1)
        current_color = RED
        for tile in tiling.tiles:
            # Alternate per tile to make
            # debugging easier
            current_color = RED if current_color == BLUE else BLUE
            context.set_source_rgb(*current_color)
            for segment in tile.segments:
                start_x = segment.start.x * x_scale_factor
                start_y = VIEW_Y_GRID_RANGE - (segment.start.y * y_scale_factor)
                end_x = segment.end.x * x_scale_factor
                end_y = VIEW_Y_GRID_RANGE - (segment.end.y * y_scale_factor)
                context.move_to(start_x, start_y)
                context.line_to(end_x, end_y)
                context.stroke()

        for ray in rays:
            current_color = RED if current_color == BLUE else BLUE
            context.set_source_rgb(*current_color)
            normalized_direction = ray.direction.normalize()
            ray_end = ray.origin + (normalized_direction * 0.25)
            start_x = ray.origin.x * x_scale_factor
            start_y = VIEW_Y_GRID_RANGE - (ray.origin.y * y_scale_factor)
            end_x = ray_end.x * x_scale_factor
            end_y = VIEW_Y_GRID_RANGE - (ray_end.y * y_scale_factor)

            context.move_to(start_x, start_y)
            context.line_to(end_x, end_y)
            context.stroke()

        return
        for segment in star_segments:
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
