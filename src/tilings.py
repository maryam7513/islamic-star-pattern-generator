from . import geometry_types as gt


def regular_square_tiling(x_grid_range: int, y_grid_range: int) -> gt.Tiling:
    """Create a grid of regular squares."""
    tiling = gt.Tiling()
    for y in range(0, y_grid_range+1):
        for x in range(0, x_grid_range+1):
            vertex_ll = gt.Vector2(x, y)
            vertex_tl = gt.Vector2(x, y+1)
            vertex_lr = gt.Vector2(x+1, y)
            vertex_tr = gt.Vector2(x+1, y+1)
            segment_b = gt.Segment(vertex_ll, vertex_lr)
            segment_t = gt.Segment(vertex_ll, vertex_tr)
            segment_l = gt.Segment(vertex_ll, vertex_tl)
            segment_r = gt.Segment(vertex_lr, vertex_tr)
            tiling.tiles.append(gt.Polygon([vertex_ll, vertex_tl, vertex_lr, vertex_tr], [segment_b, segment_t, segment_l, segment_r]))
    return tiling
