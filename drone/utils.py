from scipy.spatial import ConvexHull


def calculate_enclosed_region(coordinates):
    # Ensure we have at least 3 points to form a polygon
    if len(coordinates) < 3:
        return []

    # Use ConvexHull to find the enclosing boundary
    hull = ConvexHull(coordinates)
    enclosed_region = [coordinates[i] for i in hull.vertices]

    # Close the polygon by adding the first point at the end
    enclosed_region.append(enclosed_region[0])
    return enclosed_region
