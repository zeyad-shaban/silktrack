import numpy as np


class KalmanFilter1D:
    def __init__(self, Q_scale, R, mouse_hz=1000):
        self.Q = np.eye(2) * Q_scale
        self.R = R

        self.x = np.zeros((2, 1))
        self.F = np.array(
            [
                [1, 1 / mouse_hz],
                [0, 1],
            ]
        )
        self.H = np.array([[1, 0]])
        self.I = np.eye(2)
        self.P = np.eye(2) * 500

    def update(self, point):
        # 1. Predict
        self.x = self.F @ self.x
        self.P = self.F @ self.P @ self.F.T + self.Q
        fixed_point = self.x[0]

        # 2. Update
        K = self.P @ self.H.T / (self.H @ self.P @ self.H.T + self.R)
        self.x = self.x + K @ (point - self.H @ self.x)
        self.P = (self.I - K @ self.H) @ self.P

        return fixed_point.item()


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    N = 1000
    t = np.linspace(0, 1, N)
    y = np.sin(2 * np.pi * 3 * t) + np.random.randn(N) * 0.1

    filter = KalmanFilter1D(Q_scale=60, R=1000, mouse_hz=N)
    filtered = []
    for point in y:
        filtered.append(filter.update(point))

    plt.plot(t, y, "b", label="noisy")
    plt.plot(t, filtered, "r", label="filtered")
    plt.show()