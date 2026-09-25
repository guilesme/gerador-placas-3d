"""Pure geometry helpers for the plate outline."""

PLATE_WIDTH = 200.0
CORNER_CUT = 42.48


def normalize_cut_side(value):
    """Return one of the two supported lower-corner cut positions."""
    return "LEFT" if str(value).upper() == "LEFT" else "RIGHT"


def plate_outline_points(plate_height, cut_side="RIGHT"):
    """Return the clockwise XY outline of a plate with one lower corner cut."""
    half_w = PLATE_WIDTH / 2
    half_h = plate_height / 2

    if normalize_cut_side(cut_side) == "LEFT":
        return (
            (-half_w, half_h),
            (half_w, half_h),
            (half_w, -half_h),
            (-half_w + CORNER_CUT, -half_h),
            (-half_w, -half_h + CORNER_CUT),
        )

    return (
        (-half_w, half_h),
        (half_w, half_h),
        (half_w, -half_h + CORNER_CUT),
        (half_w - CORNER_CUT, -half_h),
        (-half_w, -half_h),
    )
