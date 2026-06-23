# Fixed-Income Risk Notes

A zero-coupon bond pays only one cash flow at maturity. Its price is the discounted value of its face value. For a given maturity, price and yield are inversely related. As time passes, if the yield is unchanged, the price of a zero-coupon bond converges toward its face value.

Duration measures the first-order sensitivity of a bond price to yield changes. Modified duration approximates percentage price sensitivity for a small yield change. Convexity measures the curvature of the price-yield relationship and improves the approximation for larger rate shocks.

DV01 or PV01 measures the approximate change in the value of a position for a one-basis-point move in yield. A fixed-income middle-office analytics process may monitor DV01 by instrument, maturity bucket, currency, and portfolio.

For larger yield shocks, exact repricing is preferred to a duration-only approximation because convexity becomes important.
