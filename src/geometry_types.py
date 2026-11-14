from dataclasses import dataclass, field
from decimal import Decimal
import math

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

    def __post_init__(self):
        self.bounds_x = (min(p.x for p in self.vertices), max(p.x for p in self.vertices))
        self.bounds_y = (min(p.y for p in self.vertices), max(p.y for p in self.vertices))

    def in_bounds(self, point: Vector2) -> bool:
        return self.bounds_x[0] < point.x < self.bounds_x[1] and self.bounds_y[0] < point.y < self.bounds_y[1]

@dataclass(frozen=True)
class Tiling:
    tiles: list[Polygon] = field(default_factory=list)

