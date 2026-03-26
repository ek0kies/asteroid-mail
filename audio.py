import pyxel


SFX_START = 0
SFX_PICKUP = 1
SFX_DELIVER = 2
SFX_HIT = 3
SFX_FAIL = 4
SFX_ALERT = 5
SFX_PAUSE = 6
BGM_PAD = 10
BGM_BASS = 11
BGM_TRACK = 0


def init_audio() -> None:
    pyxel.sounds[SFX_START].set("c2e2g2c3", "p", "6", "nnnf", 12)
    pyxel.sounds[SFX_PICKUP].set("g2b2d3", "s", "5", "nnn", 16)
    pyxel.sounds[SFX_DELIVER].set("c3e3g3c4", "p", "6", "nnnf", 10)
    pyxel.sounds[SFX_HIT].set("c1a0f0", "n", "754", "fff", 10)
    pyxel.sounds[SFX_FAIL].set("a2f2d2c2", "p", "6442", "ffff", 18)
    pyxel.sounds[SFX_ALERT].set("c3rc3r", "s", "5", "nfff", 20)
    pyxel.sounds[SFX_PAUSE].set("f2a2", "s", "5", "nf", 20)
    pyxel.sounds[BGM_PAD].set("c2g2a2g2 c2g2a2g2", "t", "3", "n", 24)
    pyxel.sounds[BGM_BASS].set("c1r c1r g0r g0r", "p", "4", "n", 24)
    pyxel.musics[BGM_TRACK].set([BGM_PAD], [BGM_BASS], [])


def play_start() -> None:
    pyxel.play(3, SFX_START)


def play_pickup() -> None:
    pyxel.play(3, SFX_PICKUP)


def play_deliver() -> None:
    pyxel.play(3, SFX_DELIVER)


def play_hit() -> None:
    pyxel.play(3, SFX_HIT)


def play_fail() -> None:
    pyxel.play(3, SFX_FAIL)


def play_alert() -> None:
    pyxel.play(3, SFX_ALERT)


def play_pause() -> None:
    pyxel.play(3, SFX_PAUSE)


def play_bgm(loop: bool = True) -> None:
    pyxel.playm(BGM_TRACK, loop=loop)


def stop_bgm() -> None:
    pyxel.stop(0)
    pyxel.stop(1)
    pyxel.stop(2)
