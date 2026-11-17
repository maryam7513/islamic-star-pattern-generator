from dataclasses import dataclass
from decimal import Decimal, DivisionByZero, InvalidOperation, getcontext
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
CONTACT_ANGLE = Decimal(math.radians(50))
DELTA = Decimal(0.0)
STEPS = 3

@dataclass(frozen=True)
class RayIntersection:
    ray1: gt.Ray
    ray2: gt.Ray
    point: gt.Vector2
    cost: Decimal
    ray1_sibling: gt.Ray
    ray2_sibling: gt.Ray

# Most of this code is borrowed from a side
# project, which I decided to turn into my
# final project.
def kaplan_star_generator(polygon: gt.Polygon) -> tuple[list[gt.Ray], gt.StarPolygon]:
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

    intersections: list[RayIntersection] = []
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

                res = test_r1.get_intersection_with(test_r2)
                if not res:
                    continue
                cost, point = res

                if not polygon.in_bounds(point):
                    continue

                r1_sibling = None
                r2_sibling = None
                for r, r_i in test_rays:
                    if r_i == r1_i and test_r1 != r:
                        r1_sibling = r
                    elif r_i == r2_i and test_r2 != r:
                        r2_sibling = r

                # All rays have siblings so this
                # should pass, this is just to silence
                # my editor's type checker.
                assert r1_sibling is not None and r2_sibling is not None
                intersections.append(RayIntersection(test_r1, test_r2, point, cost, r1_sibling, r2_sibling))

    intersections.sort(key=lambda x: x.cost)
    star_segments: list[gt.Segment] = []
    star_visible_segments: list[gt.Segment] = []
    star_points: list[gt.Vector2] = []
    encountered_rays: set[gt.Ray] = set()
    for intersection in intersections:
        if intersection.ray1 in encountered_rays or intersection.ray2 in encountered_rays:
            continue

        try:
            ray1_intersection_slope = (intersection.point.y - intersection.ray1.origin.y) / (intersection.point.x - intersection.ray1.origin.x)
        except (DivisionByZero, InvalidOperation):
            ray1_intersection_slope = 0
        try:
            ray2_intersection_slope = (intersection.ray2.origin.y - intersection.point.y) / (intersection.ray2.origin.x - intersection.point.x)
        except (DivisionByZero, InvalidOperation):
            ray2_intersection_slope = 0

        points_colinear = (ray1_intersection_slope == ray2_intersection_slope)
        if not points_colinear:
            star_points.append(intersection.point)

        if DELTA == 0.0:
            if not points_colinear:
                ray1_segment = gt.Segment(intersection.ray1.origin, intersection.point)
                ray2_segment = gt.Segment(intersection.ray2.origin, intersection.point)
                star_visible_segments.append(ray1_segment)
                star_visible_segments.append(ray2_segment)
            else:
                ray_segment = gt.Segment(intersection.ray1.origin, intersection.ray2.origin)
                star_visible_segments.append(ray_segment)
            star_points.append(intersection.ray1.origin)
            star_points.append(intersection.ray2.origin)

        if DELTA > 0.0:
            res1 = intersection.ray1.get_intersection_with(intersection.ray1_sibling)
            if res1:
                _, point = res1
                star_points.append(point)
                star_visible_segments.append(gt.Segment(intersection.ray1.origin, point))
                star_segments.append(gt.Segment(point, intersection.point))
            res2 = intersection.ray2.get_intersection_with(intersection.ray2_sibling)
            if res2:
                _, point = res2
                star_points.append(point)
                star_visible_segments.append(gt.Segment(intersection.ray2.origin, point))
                star_segments.append(gt.Segment(point, intersection.point))

        encountered_rays.add(intersection.ray1)
        encountered_rays.add(intersection.ray2)

    return [r for ray_pair in rays for r in ray_pair], gt.StarPolygon(star_points, star_segments + star_visible_segments, star_visible_segments)

def main():
    # We use the Decimal module in the Python standard
    # library because it has more precise floats, and
    # avoids floating point woes.
    getcontext().prec = 4
    tiling = tilings.regular_square_tiling(X_GRID_RANGE, Y_GRID_RANGE)

    rays: list[gt.Ray] = []
    star_segments: list[gt.Segment] = []
    for tile in tiling.tiles:
        poly = tile
        for _ in range(0, STEPS):
            new_rays, star_poly = kaplan_star_generator(poly)
            rays += new_rays
            star_segments += star_poly.segments
            star_segments += star_poly.visible_segments
            poly = star_poly

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
