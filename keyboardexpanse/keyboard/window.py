from dataclasses import dataclass
from typing import Any, List, Tuple


@dataclass
class Window:
    values: List[Tuple[float, Any]] = []
    recent_index = 0
    length_nanoseconds = 5e8  # 1s = 1e9ns

    def insert(self, time, item):

        # Expire older values
        while self.values and self.values[0][0] < time - self.length_nanoseconds:
            self.values.pop(0)
            self.recent_index -= 1

        if len(self.values) and self.values[-1] and self.values[-1][1] == item:
            self.values[-1] = (time, item)
        else:
            self.values.append((time, item))

        return

    def characters(self):
        return "+".join(c for ts, c in self.values)

    def clear(self):
        self.values = []
        self.recent_index = 0
