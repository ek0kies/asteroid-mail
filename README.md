# Asteroid Mail

![Asteroid Mail](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

一个基于 `Pyxel` 的短局街机小游戏 demo。玩家驾驶小邮船穿过小行星带，先拾取邮件核心，再在班次结束前送到投递站。

## 游戏截图

> 截图待添加

## 运行

```bash
python3 -m pip install -r requirements.txt
python3 main.py
```

## 操作

- `方向键` / `WASD`：移动
- `Space` / `Enter`：开始或重开
- `P`：暂停 / 继续
- `T`：返回标题页
- `Q`：退出

## 玩法

- 先接触 `MAIL` 信标取件
- 再前往 `DOCK` 完成投递
- 躲避漂移陨石，避免船体耐久归零
- 在 `SHIFT` 倒计时归零前尽可能完成更多投递
- 关键事件带有程序化音效，低血量和低倒计时会触发警示
- 游戏包含简短的循环 BGM，可通过暂停切断

## 项目结构

- `main.py`：游戏入口、状态机、输入和绘制
- `audio.py`：程序化音效定义与播放
- `game_entities.py`：实体定义、碰撞和随机生成逻辑
- `storage.py`：本地最高分持久化
- `PLAN.md`：实现和迭代计划

## GitHub

[![GitHub Stars](https://img.shields.io/github/stars/ek0kies/asteroid-mail?style=social)](https://github.com/ek0kies/asteroid-mail)
[![GitHub Forks](https://img.shields.io/github/forks/ek0kies/asteroid-mail?style=social)](https://github.com/ek0kies/asteroid-mail)

---

*Built with Pyxel - A Simple Game Library for Python*