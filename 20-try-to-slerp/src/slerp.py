import math

# one-dim linear parameter slerp (cos and sin both valid, yielding different behavior)
# v = start + (end - start) * sin(t * pi/2)
def slerp(a: float, b: float, t: float) -> float:
    """Sinusoidal lerp: smoothly interpolates between a and b using a sine ease in-out curve."""
    t = (1 - math.cos(t * math.pi)) / 2
    return a + (b - a) * t
