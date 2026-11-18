from collections.abc import Iterator
from dataclasses import dataclass, field
from decimal import Decimal
import math

from . import geometry_types as gt

@dataclass(frozen=True)
class TilingInstruction:
    index: int
    offset: gt.Vector2
    rotation_radians: Decimal
    rotation_pivot: gt.Vector2 | None = None

@dataclass(frozen=True)
class Tiling:
    unique_tiles: list[gt.Polygon] = field(default_factory=list)
    tiling_instructions: list[TilingInstruction] = field(default_factory=list)

    def generate_tiling(self, x_range: int, y_range: int) -> Iterator[gt.Polygon]:
        for x in range(0, x_range):
            for y in range(0, y_range):
                local_offset = gt.Vector2(Decimal(x), Decimal(y))
                for instruction in self.tiling_instructions:
                    polygon_to_tile = self.unique_tiles[instruction.index]

                    pivot = instruction.rotation_pivot if instruction.rotation_pivot is not None else None
                    polygon_to_tile = polygon_to_tile.rotate(instruction.rotation_radians, pivot)
                    polygon_to_tile = polygon_to_tile.translate(instruction.offset + local_offset)
                    yield polygon_to_tile

@dataclass(frozen=True)
class LayeredTiling(Tiling):
    additional_layers: list[Tiling] = field(default_factory=list)

def regular_square_tiling() -> Tiling:
    """Create a grid of regular squares."""
    tiling = Tiling()
    x_point = Decimal(0)
    y_point = Decimal(0)
    vertex_ll = gt.Vector2(x_point, y_point)
    vertex_tl = gt.Vector2(x_point, y_point+1)
    vertex_lr = gt.Vector2(x_point+1, y_point)
    vertex_tr = gt.Vector2(x_point+1, y_point+1)
    segment_b = gt.Segment(vertex_ll, vertex_lr)
    segment_t = gt.Segment(vertex_tl, vertex_tr)
    segment_l = gt.Segment(vertex_ll, vertex_tl)
    segment_r = gt.Segment(vertex_lr, vertex_tr)
    tiling.unique_tiles.append(gt.Polygon([vertex_ll, vertex_tl, vertex_lr, vertex_tr], [segment_b, segment_t, segment_l, segment_r]))
    tiling.tiling_instructions.append(TilingInstruction(0, gt.Vector2(Decimal(0), Decimal(0)), Decimal(0.0)))
    return tiling

def right_triangle_tiling() -> Tiling:
    """Create a grid of right triangles."""
    tiling = Tiling()
    x_point = Decimal(0)
    y_point = Decimal(0)
    vertex_ll = gt.Vector2(x_point, y_point)
    vertex_tl = gt.Vector2(x_point, y_point+1)
    vertex_lr = gt.Vector2(x_point+1, y_point)

    segment_a = gt.Segment(vertex_ll, vertex_tl)
    segment_b = gt.Segment(vertex_ll, vertex_lr)
    segment_c = gt.Segment(vertex_tl, vertex_lr)
    tiling.unique_tiles.append(gt.Polygon([vertex_ll, vertex_tl, vertex_lr], [segment_a, segment_b, segment_c]))

    tiling.tiling_instructions.append(TilingInstruction(0, gt.Vector2(Decimal(0), Decimal(0)), Decimal(0.0)))
    tiling.tiling_instructions.append(TilingInstruction(0, gt.Vector2(Decimal(0), Decimal(0)), Decimal(0.0)))
    return tiling

def regular_triangle_tiling() -> Tiling:
    """Create a grid of regular triangles."""
    tiling = Tiling()
    x_point = Decimal(0)
    y_point = Decimal(0)
    vertex_ll = gt.Vector2(x_point, y_point)
    vertex_tl = gt.Vector2(x_point, y_point+1)
    vertex_mr = gt.Vector2(x_point+1, y_point+Decimal(0.5))
    segment_a = gt.Segment(vertex_ll, vertex_tl)
    segment_b = gt.Segment(vertex_tl, vertex_mr)
    segment_c = gt.Segment(vertex_mr, vertex_ll)
    tiling.unique_tiles.append(gt.Polygon([vertex_ll, vertex_tl, vertex_mr], [segment_a, segment_b, segment_c]))
    tiling.tiling_instructions.append(TilingInstruction(0, gt.Vector2(Decimal(0), Decimal(0)), Decimal(0.0)))
    tiling.tiling_instructions.append(TilingInstruction(0, gt.Vector2(Decimal(0.0), Decimal(0.5)), Decimal(math.pi), gt.Vector2(Decimal(0.5), Decimal(0.5))))
    return tiling
