import math


def calculate_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def calculate_paths(coordinates):
    # Build a graph
    n = len(coordinates)
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            dist = calculate_distance(coordinates[i], coordinates[j])
            edges.append((dist, i, j))
    edges.sort()

    # Kruskal's algorithm for MST
    parent = list(range(n))

    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]

    mst = []
    for dist, u, v in edges:
        root_u, root_v = find(u), find(v)
        if root_u != root_v:
            parent[root_u] = root_v
            mst.append((coordinates[u], coordinates[v]))

    # Drone path (simple offset logic)
    drone_path = []
    for (p1, p2) in mst:
        dx, dy = p2[1] - p1[1], p1[0] - p2[0]
        length = math.sqrt(dx ** 2 + dy ** 2)
        offset = 0.001  # Adjust for a safe distance
        dx, dy = (dx / length) * offset, (dy / length) * offset
        drone_path.append([(p1[0] + dx, p1[1] + dy), (p2[0] + dx, p2[1] + dy)])

    return mst, drone_path
