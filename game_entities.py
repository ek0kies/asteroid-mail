from dataclasses import dataclass
import random


@dataclass
class Asteroid:
    x: float
    y: float
    vx: float
    vy: float
    radius: int
    color: int


@dataclass
class Beacon:
    x: float
    y: float


Star = tuple[int, int, int]
BlockedCircle = tuple[float, float, float]


def distance_sq(ax: float, ay: float, bx: float, by: float) -> float:
    dx = ax - bx
    dy = ay - by
    return dx * dx + dy * dy


def collides(ax: float, ay: float, ar: float, bx: float, by: float, br: float) -> bool:
    radius = ar + br
    return distance_sq(ax, ay, bx, by) <= radius * radius


def make_stars(rng: random.Random, width: int, height: int, count: int) -> list[Star]:
    colors = [1, 5, 6, 7]
    stars: list[Star] = []
    for _ in range(count):
        stars.append((rng.randrange(width), rng.randrange(height), rng.choice(colors)))
    return stars


def spawn_asteroids(
    rng: random.Random,
    width: int,
    height: int,
    count: int,
    safe_x: float,
    safe_y: float,
    safe_radius: float,
    speed_scale: float,
) -> list[Asteroid]:
    asteroids: list[Asteroid] = []
    attempts = 0
    while len(asteroids) < count and attempts < count * 80:
        attempts += 1
        x = rng.uniform(10, width - 10)
        y = rng.uniform(12, height - 10)
        if distance_sq(x, y, safe_x, safe_y) < safe_radius * safe_radius:
            continue

        vx = rng.uniform(0.35, 0.9) * speed_scale
        vy = rng.uniform(0.25, 0.8) * speed_scale
        if rng.random() < 0.5:
            vx *= -1
        if rng.random() < 0.5:
            vy *= -1

        asteroids.append(
            Asteroid(
                x=x,
                y=y,
                vx=vx,
                vy=vy,
                radius=rng.randint(4, 8),
                color=rng.choice([4, 5, 13]),
            )
        )

    return asteroids


def make_beacon(
    rng: random.Random,
    width: int,
    height: int,
    blocked: list[BlockedCircle],
) -> Beacon:
    for _ in range(200):
        x = rng.uniform(12, width - 12)
        y = rng.uniform(18, height - 12)
        is_safe = True
        for bx, by, radius in blocked:
            if distance_sq(x, y, bx, by) < radius * radius:
                is_safe = False
                break
        if is_safe:
            return Beacon(x=x, y=y)

    return Beacon(x=width / 2, y=height / 2)


def build_blocked_positions(
    player_x: float,
    player_y: float,
    asteroids: list[Asteroid],
    asteroid_padding: int = 12,
) -> list[BlockedCircle]:
    blocked = [(player_x, player_y, 26)]
    for asteroid in asteroids:
        blocked.append((asteroid.x, asteroid.y, asteroid.radius + asteroid_padding))
    return blocked
