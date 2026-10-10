"""격자 기반 A* 경로 탐색. 기계 footprint + 기둥을 장애물로 보고 통행 가능한 최단 경로를 찾는다.
동선(스파게티) 거리와 운반 시간 계산에 사용."""
import heapq, math
from functools import lru_cache


class Grid:
    def __init__(self, factory, clearance=0.6):
        site = factory["site"]
        self.g = site.get("grid_m", 1.0)
        self.nx = int(math.ceil(site["width"] / self.g))
        self.ny = int(math.ceil(site["depth"] / self.g))
        self.blocked = [[False] * self.ny for _ in range(self.nx)]
        for s in factory["stations"]:
            if s["process"] in ("raw", "fg"):
                continue  # 창고는 통행 가능(적치장 사이로 이동)
            self._block_rect(s["pos"][0] - s["size"][0] / 2 - clearance, s["pos"][1] - s["size"][1] / 2 - clearance,
                             s["size"][0] + 2 * clearance, s["size"][1] + 2 * clearance)
        for a in factory.get("ancillary", []):
            if "pos" in a and "size" in a:
                self._block_rect(a["pos"][0] - a["size"][0] / 2, a["pos"][1] - a["size"][1] / 2, a["size"][0], a["size"][1])
        for (x, y, w, d) in site.get("obstacles", []):
            self._block_rect(x - clearance, y - clearance, w + 2 * clearance, d + 2 * clearance)
        for z in site.get("zones", []):
            if z.get("type") == "office":
                xs = [p[0] for p in z["polygon"]]; ys = [p[1] for p in z["polygon"]]
                self._block_rect(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))
        self.cache = {}

    def _block_rect(self, x, y, w, d):
        for i in range(max(0, int(x / self.g)), min(self.nx, int(math.ceil((x + w) / self.g)))):
            for j in range(max(0, int(y / self.g)), min(self.ny, int(math.ceil((y + d) / self.g)))):
                self.blocked[i][j] = True

    def cell(self, p):
        i = min(self.nx - 1, max(0, int(p[0] / self.g)))
        j = min(self.ny - 1, max(0, int(p[1] / self.g)))
        return i, j

    def _nearest_free(self, c):
        if not self.blocked[c[0]][c[1]]:
            return c
        for r in range(1, 6):
            for di in range(-r, r + 1):
                for dj in range(-r, r + 1):
                    i, j = c[0] + di, c[1] + dj
                    if 0 <= i < self.nx and 0 <= j < self.ny and not self.blocked[i][j]:
                        return (i, j)
        return c

    def path(self, a, b):
        """a,b: (x,y) m. returns (points list of (x,y), length_m)"""
        key = (tuple(a), tuple(b))
        if key in self.cache:
            return self.cache[key]
        start, goal = self._nearest_free(self.cell(a)), self._nearest_free(self.cell(b))
        pts = self._astar(start, goal)
        xy = [tuple(a)] + [((i + 0.5) * self.g, (j + 0.5) * self.g) for i, j in pts[1:-1]] + [tuple(b)]
        xy = self._smooth(xy)
        length = sum(math.dist(xy[k], xy[k + 1]) for k in range(len(xy) - 1))
        self.cache[key] = (xy, length)
        return xy, length

    def _astar(self, s, g):
        if s == g:
            return [s, g]
        openh = [(0, s)]; came = {s: None}; cost = {s: 0}
        nbrs = [(1, 0, 1), (-1, 0, 1), (0, 1, 1), (0, -1, 1), (1, 1, 1.414), (1, -1, 1.414), (-1, 1, 1.414), (-1, -1, 1.414)]
        while openh:
            _, cur = heapq.heappop(openh)
            if cur == g:
                break
            for di, dj, w in nbrs:
                n = (cur[0] + di, cur[1] + dj)
                if not (0 <= n[0] < self.nx and 0 <= n[1] < self.ny) or self.blocked[n[0]][n[1]]:
                    continue
                if di and dj and (self.blocked[cur[0] + di][cur[1]] or self.blocked[cur[0]][cur[1] + dj]):
                    continue  # 모서리 끼어가기 방지
                nc = cost[cur] + w
                if nc < cost.get(n, 1e18):
                    cost[n] = nc; came[n] = cur
                    heapq.heappush(openh, (nc + math.hypot(g[0] - n[0], g[1] - n[1]), n))
        if g not in came:
            if not hasattr(self, "_warned"):
                self._warned = set()
            if (s, g) not in self._warned:
                self._warned.add((s, g)); print(f"[pathfind] 경로 없음 {s}->{g}: 직선으로 대체 (레이아웃 통로 확인 필요)")
            return [s, g]
        out = []; c = g
        while c is not None:
            out.append(c); c = came[c]
        return out[::-1]

    def _los(self, p, q):
        n = int(math.dist(p, q) / (self.g * 0.5)) + 1
        for k in range(n + 1):
            x = p[0] + (q[0] - p[0]) * k / n; y = p[1] + (q[1] - p[1]) * k / n
            i, j = self.cell((x, y))
            if self.blocked[i][j]:
                return False
        return True

    def _smooth(self, pts):
        if len(pts) < 3:
            return pts
        out = [pts[0]]; i = 0
        while i < len(pts) - 1:
            j = len(pts) - 1
            while j > i + 1 and not self._los(pts[i], pts[j]):
                j -= 1
            out.append(pts[j]); i = j
        return out
