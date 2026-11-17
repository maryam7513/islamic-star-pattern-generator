from decimal import Decimal, getcontext
import itertools
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
CONTACT_ANGLE = Decimal(math.radians(25))
DELTA = Decimal(0.1)
STEP = 1


# Most of this code is borrowed from a side
# project, which I decided to turn into my
# final project.
def get_ray_intersection(ray1: gt.Ray, ray2: gt.Ray) -> tuple[Decimal, Decimal] | None:
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
    rays: list[tuple[gt.Ray, gt.Ray]] = []
    for i in range(n):
        segment = polygon.segments[i]
        midpoint = segment.midpoint()

        edge_dir = (segment.end - segment.start).normalize()
        origin_a = midpoint - (edge_dir * DELTA)
        origin_b = midpoint + (edge_dir * DELTA)

        # Rotate by 90 degrees to get the normal
        inward_normal = gt.Vector2(edge_dir.y, -edge_dir.x)
        if not polygon.in_bounds(midpoint + inward_normal * Decimal(0.01)):
            inward_normal = gt.Vector2(-edge_dir.y, edge_dir.x)

        sin_of_angle = Decimal(math.sin(CONTACT_ANGLE))
        cos_of_angle = Decimal(math.cos(CONTACT_ANGLE))
        direction_a = (edge_dir * cos_of_angle) + (inward_normal * sin_of_angle)
        direction_b = (edge_dir * -cos_of_angle) + (inward_normal * sin_of_angle)

        rays.append((gt.Ray(origin_a, direction_a), gt.Ray(origin_b, direction_b)))

    intersections_and_costs: list[tuple[gt.Ray, gt.Ray, gt.Vector2, Decimal]] = []
    for i, (ray1, ray2) in enumerate(rays):
        for j, (ray3, ray4) in enumerate(rays):
            # Ignore if the pairs are the same
            if i == j:
                continue

            test_rays = [(ray1, i), (ray2, i), (ray3, j), (ray4, j)]
            for (test_r1, r1_i), (test_r2, r2_i) in itertools.combinations(test_rays, 2):
                # Do not count intersections
                # between rays of the same pair
                if r1_i == r2_i:
                    continue
                if test_r1.origin == test_r2.origin:
                    continue
                res = get_ray_intersection(test_r1, test_r2)
                if not res:
                    continue
                u, v = res
                cost = u + v
                point = test_r1.origin + test_r1.direction * u

                if not polygon.in_bounds(point):
                    continue

                intersections_and_costs.append((test_r1, test_r2, point, cost))

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

    return [r for ray_pair in rays for r in ray_pair], star_segments

def main():
    # We use the Decimal module in the Python standard
    # library because it has more precise floats, and
    # avoids floating point woes.
    getcontext().prec = 4
    tiling = tilings.regular_triangle_tiling(X_GRID_RANGE, Y_GRID_RANGE)

    rays: list[gt.Ray] = []
    star_segments: list[gt.Segment] = []
    for tile in tiling.tiles:
        new_rays, new_segments = kaplan_star_generator(tile)
        rays += new_rays
        star_segments += new_segments

    x_scale_factor, y_scale_factor = Decimal(VIEW_X_GRID_RANGE / X_GRID_RANGE), Decimal(VIEW_Y_GRID_RANGE / Y_GRID_RANGE)
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
                start_x = float(segment.start.x * x_scale_factor)
                start_y = float(VIEW_Y_GRID_RANGE - (segment.start.y * y_scale_factor))
                end_x = float(segment.end.x * x_scale_factor)
                end_y = float(VIEW_Y_GRID_RANGE - (segment.end.y * y_scale_factor))
                context.move_to(start_x, start_y)
                context.line_to(end_x, end_y)
                context.stroke()

        for ray in rays:
            current_color = RED if current_color == BLUE else BLUE
            context.set_source_rgb(*current_color)
            normalized_direction = ray.direction.normalize()
            ray_end = ray.origin + (normalized_direction * Decimal(0.25))
            start_x = float(ray.origin.x * x_scale_factor)
            start_y = float(VIEW_Y_GRID_RANGE - (ray.origin.y * y_scale_factor))
            end_x = float(ray_end.x * x_scale_factor)
            end_y = float(VIEW_Y_GRID_RANGE - (ray_end.y * y_scale_factor))

            context.move_to(start_x, start_y)
            context.line_to(end_x, end_y)
            context.stroke()

        context.set_source_rgb(0, 0, 0)
        for segment in star_segments:
            # We have to flip the Y-coordinates for SVG
            start_x = float(segment.start.x * x_scale_factor)
            start_y = float(VIEW_Y_GRID_RANGE - (segment.start.y * y_scale_factor))
            end_x = float(segment.end.x * x_scale_factor)
            end_y = float(VIEW_Y_GRID_RANGE - (segment.end.y * y_scale_factor))

            context.move_to(start_x, start_y)
            context.line_to(end_x, end_y)
            context.stroke()

if __name__ == "__main__":
    main()
