from dataclasses import dataclass, field
from decimal import Decimal
import math
import random

@dataclass(frozen=True)
class Vector2:
    x: Decimal
    y: Decimal

    def __add__(self, other: 'Vector2') -> 'Vector2':
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Vector2') -> 'Vector2':
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: Decimal) -> 'Vector2':
        return Vector2(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar: Decimal) -> 'Vector2':
        return Vector2(self.x / scalar, self.y / scalar)

    def cross(self, other: 'Vector2') -> Decimal:
        return self.x * other.y - self.y * other.x

    def magnitude(self) -> Decimal:
        return Decimal(math.hypot(self.x, self.y))

    def normalize(self) -> 'Vector2':
        return self / self.magnitude()

@dataclass(frozen=True)
class Segment:
    start: Vector2
    end: Vector2

    def midpoint(self) -> Vector2:
        return (self.start + self.end) / Decimal(2)

@dataclass(frozen=True)
class Ray:
    origin: Vector2
    direction: Vector2

@dataclass
class Polygon:
    vertices: list[Vector2]
    segments: list[Segment]
    bounds_x: tuple[Decimal, Decimal] = field(init=False)
    bounds_y: tuple[Decimal, Decimal] = field(init=False)
    bound_rect_segments: list[Segment] = field(init=False)

    def __post_init__(self):
        self.bounds_x = (min(p.x for p in self.vertices), max(p.x for p in self.vertices))
        self.bounds_y = (min(p.y for p in self.vertices), max(p.y for p in self.vertices))

        # Segments are specifically in clockwise order,
        # so bounds checks can be simplified.
        self.bound_rect_segments = [
            Segment(Vector2(self.bounds_x[0], self.bounds_y[0]), Vector2(self.bounds_x[1], self.bounds_y[0])),
            Segment(Vector2(self.bounds_x[1], self.bounds_y[0]), Vector2(self.bounds_x[1], self.bounds_y[1])),
            Segment(Vector2(self.bounds_x[1], self.bounds_y[1]), Vector2(self.bounds_x[0], self.bounds_y[1])),
            Segment(Vector2(self.bounds_x[0], self.bounds_y[1]), Vector2(self.bounds_x[0], self.bounds_y[0])),
        ]

    def in_bounds(self, point: Vector2) -> bool:
        test_points: list[Vector2] = []
        for segment in self.bound_rect_segments:
            distance = random.random()
            midpoint = segment.midpoint()
            edge_dir = (segment.end - segment.start).normalize()
            outward_normal = Vector2(edge_dir.y, -edge_dir.x)
            test_points.append(Vector2(midpoint.x + (outward_normal.x * Decimal(distance)), midpoint.y + (outward_normal.y * Decimal(distance))))

        test_segments = [Segment(point, t) for t in test_points]

        # To check if segments intersect, we
        # use a simple algorithm that, given
        # two segments AB and CD, checks if
        # the points A, C, and D are the opposite
        # orientation of B, C, and D (and likewise,
        # if the orientation of A, B, and C is opposite
        # of A, B, and D). This is borrowed from
        # Bryce Boe: https://bryceboe.com/2006/10/23/line-segment-intersection-algorithm/
        def is_counterclockwise(a: Vector2, b: Vector2, c: Vector2) -> bool:
            return (c.y - a.y)*(b.x - a.x) > (b.y-a.y)*(c.x-a.x)

        def segments_intersect(ab: Segment, cd: Segment) -> bool:
            return (is_counterclockwise(ab.start, cd.start, cd.end) != is_counterclockwise(ab.end, cd.start, cd.end)
                and is_counterclockwise(ab.start, ab.end, cd.start) != is_counterclockwise(ab.start, ab.end, cd.end))

        intersection_test_results: list[bool] = []
        for segment in test_segments:
            intersections = 0
            for poly_segment in self.segments:
                if not segments_intersect(segment, poly_segment):
                    continue
                intersections += 1

            # Odd number of intersections means
            # the point is inside the polygon.
            if intersections % 2 != 0:
                intersection_test_results.append(True)
            else:
                intersection_test_results.append(False)
        return intersection_test_results.count(True) > intersection_test_results.count(False)

@dataclass
class StarPolygon(Polygon):
    visible_segments: list[Segment] = field(default_factory=list)

@dataclass(frozen=True)
class Tiling:
    tiles: list[Polygon] = field(default_factory=list)

