import random

import pyxel

from audio import (
    init_audio,
    play_alert,
    play_bgm,
    play_deliver,
    play_fail,
    play_hit,
    play_pause,
    play_pickup,
    play_start,
    stop_bgm,
)
from game_entities import Asteroid, Beacon, build_blocked_positions, collides, make_beacon, make_stars, spawn_asteroids
from storage import load_best_score, save_best_score


FPS = 60
TITLE = "title"
PLAYING = "playing"
PAUSED = "paused"
GAME_OVER = "game_over"


class App:
    def __init__(self) -> None:
        self.width = 160
        self.height = 120
        self.player_radius = 4
        self.mail_radius = 5
        self.rng = random.Random()

        pyxel.init(self.width, self.height, title="Asteroid Mail", fps=FPS)
        init_audio()
        play_bgm()

        self.best_score = load_best_score()
        self.state = TITLE
        self.game_over_reason = "SHIFT OVER"
        self.message = ""
        self.message_timer = 0
        self.title_tick = 0
        self.last_shift_alert_second = -1
        self.last_eta_alert_second = -1
        self.stars = make_stars(self.rng, self.width, self.height, 40)
        self.title_asteroids = self.spawn_asteroids(5, self.width / 2, self.height / 2, 28, 0.8)
        self.reset_run()

        pyxel.run(self.update, self.draw)

    def reset_run(self) -> None:
        self.player_x = self.width / 2
        self.player_y = self.height / 2
        self.player_dx = 1.0
        self.player_dy = 0.0
        self.trail: list[tuple[float, float]] = []
        self.hull = 3
        self.score = 0
        self.deliveries = 0
        self.shift_timer = 45 * FPS
        self.delivery_timer = 0
        self.invuln_timer = 0
        self.flash_timer = 0
        self.has_cargo = False
        self.last_shift_alert_second = -1
        self.last_eta_alert_second = -1
        self.asteroids = self.spawn_asteroids(4, self.player_x, self.player_y, 22, 1.0)
        self.pickup = self.make_beacon(self.blocked_positions())
        self.dock = self.make_beacon(self.blocked_positions() + [(self.pickup.x, self.pickup.y, 30)])
        self.set_message("Collect the mail core", 120)

    def set_message(self, text: str, duration: int) -> None:
        self.message = text
        self.message_timer = duration

    def spawn_asteroids(
        self,
        count: int,
        safe_x: float,
        safe_y: float,
        safe_radius: float,
        speed_scale: float,
    ) -> list[Asteroid]:
        return spawn_asteroids(
            self.rng,
            self.width,
            self.height,
            count,
            safe_x,
            safe_y,
            safe_radius,
            speed_scale,
        )

    def make_beacon(self, blocked: list[tuple[float, float, float]]) -> Beacon:
        return make_beacon(self.rng, self.width, self.height, blocked)

    def blocked_positions(self) -> list[tuple[float, float, float]]:
        return build_blocked_positions(self.player_x, self.player_y, self.asteroids)

    def start_game(self) -> None:
        self.state = PLAYING
        self.reset_run()
        play_bgm()
        play_start()

    def end_game(self, reason: str) -> None:
        self.state = GAME_OVER
        self.game_over_reason = reason
        if self.score > self.best_score:
            self.best_score = self.score
            save_best_score(self.best_score)
        play_fail()
        self.set_message("Press SPACE to fly again", 9999)

    def update(self) -> None:
        self.title_tick += 1

        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        if self.state == TITLE:
            self.update_title()
            return

        if self.state == PAUSED:
            self.update_paused()
            return

        if self.state == GAME_OVER:
            self.update_game_over()
            return

        self.update_playing()

    def update_title(self) -> None:
        self.move_asteroids(self.title_asteroids)
        if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_RETURN):
            self.start_game()

    def update_game_over(self) -> None:
        self.move_asteroids(self.asteroids)
        if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_R):
            self.start_game()
        elif pyxel.btnp(pyxel.KEY_T):
            self.state = TITLE
            self.title_asteroids = self.spawn_asteroids(5, self.width / 2, self.height / 2, 28, 0.8)

    def update_paused(self) -> None:
        if pyxel.btnp(pyxel.KEY_P):
            self.state = PLAYING
            play_pause()
            play_bgm()
        elif pyxel.btnp(pyxel.KEY_T):
            self.state = TITLE
            self.title_asteroids = self.spawn_asteroids(5, self.width / 2, self.height / 2, 28, 0.8)
            play_bgm()

    def update_playing(self) -> None:
        if pyxel.btnp(pyxel.KEY_P):
            self.state = PAUSED
            play_pause()
            stop_bgm()
            return

        dx = 0.0
        dy = 0.0
        speed = 1.55

        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_A):
            dx -= speed
        if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_D):
            dx += speed
        if pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.KEY_W):
            dy -= speed
        if pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.KEY_S):
            dy += speed

        if dx != 0.0 and dy != 0.0:
            dx *= 0.72
            dy *= 0.72

        if dx != 0.0 or dy != 0.0:
            self.player_dx = dx
            self.player_dy = dy

        self.player_x = (self.player_x + dx) % self.width
        self.player_y = (self.player_y + dy) % self.height

        self.trail.append((self.player_x, self.player_y))
        if len(self.trail) > 14:
            self.trail.pop(0)

        self.move_asteroids(self.asteroids)

        self.shift_timer -= 1
        if self.shift_timer <= 0:
            self.end_game("SHIFT OVER")
            return

        if self.message_timer > 0:
            self.message_timer -= 1

        if self.invuln_timer > 0:
            self.invuln_timer -= 1
        if self.flash_timer > 0:
            self.flash_timer -= 1

        self.handle_mail_targets()
        self.handle_asteroid_hits()
        self.handle_alerts()

    def handle_mail_targets(self) -> None:
        if not self.has_cargo:
            if collides(self.player_x, self.player_y, self.player_radius, self.pickup.x, self.pickup.y, self.mail_radius):
                self.has_cargo = True
                self.delivery_timer = max(6 * FPS, 15 * FPS - self.deliveries * 20)
                blocked = self.blocked_positions()
                blocked.append((self.pickup.x, self.pickup.y, 40))
                self.dock = self.make_beacon(blocked)
                self.set_message("Mail loaded. Reach the dock", 90)
                play_pickup()
        else:
            self.delivery_timer -= 1
            if self.delivery_timer <= 0:
                self.has_cargo = False
                self.score = max(0, self.score - 8)
                self.pickup = self.make_beacon(self.blocked_positions())
                self.last_eta_alert_second = -1
                self.set_message("Delivery lost. New route opened", 90)
                play_fail()
                return

            if collides(self.player_x, self.player_y, self.player_radius, self.dock.x, self.dock.y, self.mail_radius + 1):
                bonus = 12 + max(0, self.delivery_timer // FPS)
                self.score += bonus
                self.deliveries += 1
                self.shift_timer = min(60 * FPS, self.shift_timer + 7 * FPS)
                self.has_cargo = False
                self.last_eta_alert_second = -1
                self.pickup = self.make_beacon(self.blocked_positions())
                self.maybe_expand_hazard()
                self.set_message(f"Delivered +{bonus}", 75)
                play_deliver()

    def maybe_expand_hazard(self) -> None:
        if self.deliveries % 2 != 0:
            return

        new_asteroid = self.spawn_asteroids(1, self.player_x, self.player_y, 26, 1.0 + self.deliveries * 0.05)
        if new_asteroid:
            self.asteroids.extend(new_asteroid)

    def handle_asteroid_hits(self) -> None:
        if self.invuln_timer > 0:
            return

        for asteroid in self.asteroids:
            if collides(
                self.player_x,
                self.player_y,
                self.player_radius,
                asteroid.x,
                asteroid.y,
                asteroid.radius,
            ):
                self.hull -= 1
                self.invuln_timer = 60
                self.flash_timer = 12
                self.player_x = (self.player_x - asteroid.vx * 5) % self.width
                self.player_y = (self.player_y - asteroid.vy * 5) % self.height
                self.set_message("Hull hit. Stay clear", 60)
                if self.hull <= 0:
                    self.end_game("HULL LOST")
                else:
                    play_hit()
                return

    def handle_alerts(self) -> None:
        shift_left = max(0, self.shift_timer // FPS)
        if not self.has_cargo:
            self.last_eta_alert_second = -1
            if shift_left <= 10 and shift_left != self.last_shift_alert_second:
                self.last_shift_alert_second = shift_left
                play_alert()
            return

        eta_left = max(0, self.delivery_timer // FPS)
        if eta_left <= 3 and eta_left != self.last_eta_alert_second:
            self.last_eta_alert_second = eta_left
            play_alert()
            return

        if shift_left <= 10 and shift_left != self.last_shift_alert_second:
            self.last_shift_alert_second = shift_left
            play_alert()

    def move_asteroids(self, asteroids: list[Asteroid]) -> None:
        for asteroid in asteroids:
            asteroid.x = (asteroid.x + asteroid.vx) % self.width
            asteroid.y = (asteroid.y + asteroid.vy) % self.height

    def draw(self) -> None:
        pyxel.cls(0)
        self.draw_stars()

        if self.state == TITLE:
            self.draw_title()
        elif self.state == PAUSED:
            self.draw_playfield(dim=True)
            self.draw_paused()
        elif self.state == GAME_OVER:
            self.draw_playfield(dim=True)
            self.draw_game_over()
        else:
            self.draw_playfield(dim=False)

    def draw_stars(self) -> None:
        for index, (x, y, color) in enumerate(self.stars):
            blink = (self.title_tick // (6 + index % 5)) % 2
            pyxel.pset(x, y, color if blink == 0 else 7)

    def draw_title(self) -> None:
        for asteroid in self.title_asteroids:
            self.draw_asteroid(asteroid)

        pyxel.rect(14, 18, 132, 82, 1)
        pyxel.rectb(14, 18, 132, 82, 6)
        pyxel.text(43, 28, "ASTEROID MAIL", 10)
        pyxel.text(31, 44, "PICK UP CORES, DODGE ROCKS,", 7)
        pyxel.text(38, 54, "AND DELIVER BEFORE SHIFT END.", 7)
        pyxel.text(35, 72, "MOVE  ARROWS / WASD", 11)
        pyxel.text(24, 82, "SPACE START   P PAUSE IN RUN", 10 if (self.title_tick // 20) % 2 == 0 else 7)
        pyxel.text(44, 92, f"BEST {self.best_score:03d}", 6)

    def draw_playfield(self, dim: bool) -> None:
        target = self.dock if self.has_cargo else self.pickup
        target_color = 10 if self.has_cargo else 9
        self.draw_target_line(target, target_color)

        if not self.has_cargo:
            self.draw_pickup()
        else:
            self.draw_dock()

        for asteroid in self.asteroids:
            self.draw_asteroid(asteroid)

        self.draw_player(dim)
        self.draw_hud()
        self.draw_warning_banner()

        if self.message_timer > 0:
            pyxel.text(34, 109, self.message[:26], 7)

    def draw_target_line(self, target: Beacon, color: int) -> None:
        pyxel.line(int(self.player_x), int(self.player_y), int(target.x), int(target.y), color)

    def draw_pickup(self) -> None:
        pulse = (self.title_tick // 8) % 3
        color = 9 if pulse != 1 else 10
        x = int(self.pickup.x)
        y = int(self.pickup.y)
        pyxel.circ(x, y, 5 + pulse, color)
        pyxel.circb(x, y, 8 + pulse, 7)
        pyxel.text(x - 8, y - 13, "MAIL", 7)

    def draw_dock(self) -> None:
        pulse = (self.title_tick // 6) % 3
        x = int(self.dock.x)
        y = int(self.dock.y)
        pyxel.circb(x, y, 7 + pulse, 10)
        pyxel.rect(x - 4, y - 4, 8, 8, 10)
        pyxel.rectb(x - 6, y - 6, 12, 12, 7)
        pyxel.text(x - 8, y - 15, "DOCK", 7)

    def draw_asteroid(self, asteroid: Asteroid) -> None:
        x = int(asteroid.x)
        y = int(asteroid.y)
        pyxel.circ(x, y, asteroid.radius, asteroid.color)
        pyxel.circb(x, y, asteroid.radius, 7)
        pyxel.pset(x - 1, y - asteroid.radius + 2, 1)
        pyxel.pset(x + asteroid.radius - 1, y + 1, 1)
        pyxel.pset(x - asteroid.radius + 1, y + 2, 1)

    def draw_player(self, dim: bool) -> None:
        for index, (tx, ty) in enumerate(self.trail):
            color = 12 if index >= len(self.trail) // 2 else 5
            pyxel.circ(tx, ty, 1, color)

        if self.invuln_timer > 0 and (self.invuln_timer // 4) % 2 == 0:
            return

        x = int(self.player_x)
        y = int(self.player_y)
        if self.flash_timer > 0 and (self.flash_timer // 2) % 2 == 0:
            body_color = 8
        else:
            body_color = 11 if not dim else 7
        thrust_color = 8 if (self.title_tick // 3) % 2 == 0 else 10

        pyxel.rect(x - 3, y - 2, 6, 4, body_color)
        pyxel.rectb(x - 4, y - 3, 8, 6, 7)
        pyxel.pset(x + self.direction_x(), y + self.direction_y(), 10)
        pyxel.pset(x - self.direction_x(), y - self.direction_y(), thrust_color)

    def direction_x(self) -> int:
        if self.player_dx > 0.2:
            return 4
        if self.player_dx < -0.2:
            return -4
        return 0

    def direction_y(self) -> int:
        if self.player_dy > 0.2:
            return 3
        if self.player_dy < -0.2:
            return -3
        return 0

    def draw_hud(self) -> None:
        pyxel.rect(4, 4, 70, 22, 1)
        pyxel.rectb(4, 4, 70, 22, 6)
        pyxel.text(8, 8, f"SCORE {self.score:03d}", 7)
        pyxel.text(8, 16, f"MAIL {'YES' if self.has_cargo else 'NO '}", 10 if self.has_cargo else 7)

        pyxel.rect(87, 4, 69, 22, 1)
        pyxel.rectb(87, 4, 69, 22, 6)
        pyxel.text(91, 8, f"HULL {self.hull}", 8 if self.hull == 1 else 7)
        pyxel.text(91, 16, f"STOPS {self.deliveries}", 7)

        time_left = max(0, self.shift_timer // FPS)
        shift_color = 8 if time_left <= 10 and (self.title_tick // 8) % 2 == 0 else 6
        pyxel.text(58, 30, f"SHIFT {time_left:02d}", shift_color)
        if self.has_cargo:
            eta_left = max(0, self.delivery_timer // FPS)
            eta_color = 8 if eta_left <= 3 and (self.title_tick // 8) % 2 == 0 else 10
            pyxel.text(97, 30, f"ETA {eta_left:02d}", eta_color)

    def draw_warning_banner(self) -> None:
        warning = ""
        color = 8

        if self.hull == 1:
            warning = "LAST HULL"
        elif self.has_cargo and self.delivery_timer // FPS <= 3:
            warning = "DOCK NOW"
        elif self.shift_timer // FPS <= 10:
            warning = "SHIFT CRITICAL"

        if warning and (self.title_tick // 8) % 2 == 0:
            pyxel.rect(46, 36, 68, 10, 1)
            pyxel.rectb(46, 36, 68, 10, color)
            pyxel.text(60, 39, warning, color)

    def draw_paused(self) -> None:
        pyxel.rect(22, 30, 116, 56, 0)
        pyxel.rectb(22, 30, 116, 56, 6)
        pyxel.text(62, 40, "PAUSED", 10)
        pyxel.text(37, 54, "P RESUME   T TITLE", 7)
        pyxel.text(30, 66, "SHIFT AND ETA ARE FROZEN", 6)

    def draw_game_over(self) -> None:
        pyxel.rect(22, 30, 116, 56, 0)
        pyxel.rectb(22, 30, 116, 56, 8)
        pyxel.text(49, 40, self.game_over_reason, 8)
        pyxel.text(42, 54, f"FINAL SCORE {self.score:03d}", 7)
        pyxel.text(40, 64, f"BEST SCORE  {self.best_score:03d}", 10)
        pyxel.text(34, 74, "SPACE RESTART  T TITLE", 6)


App()
