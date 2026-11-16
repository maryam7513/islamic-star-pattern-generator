from decimal import Decimal

from . import geometry_types as gt


def regular_square_tiling(x_grid_range: int, y_grid_range: int) -> gt.Tiling:
    """Create a grid of regular squares."""
    tiling = gt.Tiling()
    for y in range(0, y_grid_range):
        for x in range(0, x_grid_range):
            x_point = Decimal(x)
            y_point = Decimal(y)
            vertex_ll = gt.Vector2(x_point, y_point)
            vertex_tl = gt.Vector2(x_point, y_point+1)
            vertex_lr = gt.Vector2(x_point+1, y_point)
            vertex_tr = gt.Vector2(x_point+1, y_point+1)
            segment_b = gt.Segment(vertex_ll, vertex_lr)
            segment_t = gt.Segment(vertex_tl, vertex_tr)
            segment_l = gt.Segment(vertex_ll, vertex_tl)
            segment_r = gt.Segment(vertex_lr, vertex_tr)
            tiling.tiles.append(gt.Polygon([vertex_ll, vertex_tl, vertex_lr, vertex_tr], [segment_b, segment_t, segment_l, segment_r]))
    return tiling

def right_triangle_tiling(x_grid_range: int, y_grid_range: int) -> gt.Tiling:
    """Create a grid of right triangles."""
    tiling = gt.Tiling()
    for y in range(0, y_grid_range):
        for x in range(0, x_grid_range):
            x_point = Decimal(x)
            y_point = Decimal(y)
            vertex_ll = gt.Vector2(x_point, y_point)
            vertex_tl = gt.Vector2(x_point, y_point+1)
            vertex_lr = gt.Vector2(x_point+1, y_point)
            vertex_tr = gt.Vector2(x_point+1, y_point+1)

            segment_a = gt.Segment(vertex_ll, vertex_tl)
            segment_b = gt.Segment(vertex_ll, vertex_lr)
            segment_c = gt.Segment(vertex_tl, vertex_lr)
            tiling.tiles.append(gt.Polygon([vertex_ll, vertex_tl, vertex_lr], [segment_a, segment_b, segment_c]))

            segment_a = gt.Segment(vertex_tl, vertex_tr)
            segment_b = gt.Segment(vertex_tr, vertex_lr)
            segment_c = gt.Segment(vertex_tl, vertex_lr)
            tiling.tiles.append(gt.Polygon([vertex_tr, vertex_tl, vertex_lr], [segment_a, segment_b, segment_c]))
    return tiling

def regular_triangle_tiling(x_grid_range: int, y_grid_range: int) -> gt.Tiling:
    """Create a grid of regular triangles."""
    tiling = gt.Tiling()
    for y in range(0, y_grid_range):
        for x in range(0, x_grid_range):
            x_point = Decimal(x)
            y_point = Decimal(y)
            vertex_ll = gt.Vector2(x_point, y_point)
            vertex_tl = gt.Vector2(x_point, y_point+1)
            vertex_mr = gt.Vector2(x_point+1, y_point+Decimal(0.5))
            segment_a = gt.Segment(vertex_ll, vertex_tl)
            segment_b = gt.Segment(vertex_tl, vertex_mr)
            segment_c = gt.Segment(vertex_mr, vertex_ll)
            tiling.tiles.append(gt.Polygon([vertex_ll, vertex_tl, vertex_mr], [segment_a, segment_b, segment_c]))

            vertex_mr_2 = gt.Vector2(x_point+1, y_point+Decimal(1.5))
            segment_a = gt.Segment(vertex_mr, vertex_mr_2)
            segment_b = gt.Segment(vertex_mr_2, vertex_tl)
            segment_c = gt.Segment(vertex_tl, vertex_mr)
            tiling.tiles.append(gt.Polygon([vertex_mr, vertex_mr_2, vertex_tl], [segment_a, segment_b, segment_c]))
    return tiling
