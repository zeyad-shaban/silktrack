from anti_jitter import AntiJitter

if __name__ == "__main__":
    anti_jitter = AntiJitter(Q_scale=110, R=1500, mouse_hz=1000)
    anti_jitter.run()
