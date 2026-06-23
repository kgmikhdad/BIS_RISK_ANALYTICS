from src.cbrap.fixed_income import analytics, bond_price


def test_zero_coupon_price_100_face_5pct_one_year():
    price = bond_price(100, 0.0, 0.05, 1.0, 1, "zero_coupon")
    assert abs(price - 95.238095) < 1e-5


def test_price_decreases_when_yield_increases():
    low_yield_price = bond_price(100, 0.0, 0.05, 1.0, 1, "zero_coupon")
    high_yield_price = bond_price(100, 0.0, 0.10, 1.0, 1, "zero_coupon")
    assert high_yield_price < low_yield_price


def test_analytics_positive_duration_and_dv01():
    a = analytics(100, 0.03, 0.04, 5.0, 2, "coupon")
    assert a.price > 0
    assert a.modified_duration > 0
    assert a.dv01 > 0
