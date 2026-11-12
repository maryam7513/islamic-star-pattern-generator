from dataclasses import dataclass, field
import math

@dataclass(frozen=True)
class Vector2:
    x: float
    y: float

    def __add__(self, other: 'Vector2') -> 'Vector2':
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Vector2') -> 'Vector2':
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> 'Vector2':
        return Vector2(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar: float) -> 'Vector2':
        return Vector2(self.x / scalar, self.y / scalar)

    def cross(self, other: 'Vector2') -> float:
        return self.x * other.y - self.y * other.x

    def magnitude(self) -> float:
        return math.hypot(self.x, self.y)

    def normalize(self) -> 'Vector2':
        return self / self.magnitude()

@dataclass(frozen=True)
class Segment:
    start: Vector2
    end: Vector2

    def midpoint(self) -> Vector2:
        return (self.start + self.end) / 2

@dataclass(frozen=True)
class Ray:
    origin: Vector2
    direction: Vector2

@dataclass(frozen=True)
class Polygon:
    vertices: list[Vector2]
    segments: list[Segment]

@dataclass(frozen=True)
class Tiling:
    tiles: list[Polygon] = field(default_factory=list)

