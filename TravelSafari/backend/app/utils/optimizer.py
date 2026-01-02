# backend/app/utils/optimizer.py

import random
import math
from typing import List, Dict

# -----------------------------
# Haversine Distance Function
# -----------------------------
def haversine(a: Dict[str, float], b: Dict[str, float]) -> float:
    """
    Calculate great-circle distance between two points (lat/lng) in kilometers.
    """
    R = 6371.0  # Earth radius in km
    lat1, lon1 = math.radians(a["lat"]), math.radians(a["lng"])
    lat2, lon2 = math.radians(b["lat"]), math.radians(b["lng"])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return R * (2 * math.atan2(math.sqrt(h), math.sqrt(1 - h)))

# -----------------------------
# Total Distance for a Route
# -----------------------------
def total_distance(route: List[int], points: List[Dict[str, float]]) -> float:
    """
    Compute total distance of a route given a list of point indices.
    """
    return sum(haversine(points[route[i]], points[route[i + 1]]) for i in range(len(route) - 1))

# -----------------------------
# Genetic Algorithm for Route Optimization
# -----------------------------
def genetic_algorithm(points: List[Dict[str, float]], generations: int = 200, population_size: int = 100) -> List[int]:
    """
    Simple GA to find an approximate shortest path visiting all points.
    """
    num_points = len(points)
    if num_points < 2:
        return list(range(num_points))

    # Initial population: start fixed at index 0
    population = [
        [0] + random.sample(range(1, num_points), num_points - 1)
        for _ in range(population_size)
    ]

    for _ in range(generations):
        # Sort by fitness (shortest distance)
        population.sort(key=lambda r: total_distance(r, points))
        next_gen = population[:10]  # elite selection

        # Crossover
        while len(next_gen) < population_size:
            a, b = random.sample(population[:20], 2)
            cut1, cut2 = sorted(random.sample(range(1, num_points), 2))
            child = [None] * num_points
            child[cut1:cut2] = a[cut1:cut2]

            pos = cut2
            for gene in b:
                if gene not in child:
                    if pos >= num_points:
                        pos = 0
                    child[pos] = gene
                    pos += 1

            next_gen.append(child)

        # Mutation
        for route in next_gen[10:]:
            if random.random() < 0.2:
                i, j = random.sample(range(1, num_points), 2)
                route[i], route[j] = route[j], route[i]

        population = next_gen

    # Return the best route
    return min(population, key=lambda r: total_distance(r, points))

# -----------------------------
# Optimize Route Wrapper
# -----------------------------
def optimize_route(locations: List[Dict[str, float]]) -> Dict[str, float or List[Dict[str, float]]]:
    """
    Input: list of locations [{"lat":.., "lng":..}, ...]
    Output: dict with optimized route and total distance
    """
    if len(locations) < 2:
        return {"route": locations, "total_distance": 0.0}

    for p in locations:
        if "lat" not in p or "lng" not in p:
            raise ValueError("Each location must contain lat and lng")

    order = genetic_algorithm(locations)
    optimized = [locations[i] for i in order]
    dist = total_distance(order, locations)

    return {"route": optimized, "total_distance": dist}

# -----------------------------
# Test
# -----------------------------
if __name__ == "__main__":
    sample_locations = [
        {"lat": 28.61, "lng": 77.21},  # Delhi
        {"lat": 27.17, "lng": 78.04},  # Agra
        {"lat": 26.85, "lng": 80.95},  # Lucknow
    ]
    result = optimize_route(sample_locations)
    print("Optimized Route:", result["route"])
    print("Total Distance:", result["total_distance"])
