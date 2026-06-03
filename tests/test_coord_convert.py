from lib.coord_convert_wgs84_to_gcj02 import transform


def test_transform_china_interior_offsets():
    lng, lat = 118.5174286, 28.99795452
    g_lng, g_lat = transform(lng, lat)
    assert g_lng != lng or g_lat != lat
    assert 118.4 < g_lng < 118.7
    assert 28.9 < g_lat < 29.1


def test_transform_outside_china_unchanged():
    lng, lat = 10.0, 10.0
    assert transform(lng, lat) == (lng, lat)
