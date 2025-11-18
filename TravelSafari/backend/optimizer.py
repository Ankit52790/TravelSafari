# backend/optimizer.py
import random
import math
from typing import List, Dict, Any

def haversine(a: Dict[str, float], b: Dict[str, float]) -> float:
    """Great-circle distance between two lat/lng points (in km)."""
    R = 6371.0
    lat1, lon1 = math.radians(a["lat"]), math.radians(a["lng"])
    lat2, lon2 = math.radians(b["lat"]), math.radians(b["lng"])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a_ = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a_), math.sqrt(1 - a_))
    return R * c

def total_distance(route: List[int], points: List[Dict[str, float]]) -> float:
    dist = 0.0
    for i in range(len(route) - 1):
        dist += haversine(points[route[i]], points[route[i + 1]])
    return dist

def genetic_algorithm(
    points: List[Dict[str, float]],
    generations: int = 200,
    population_size: int = 100,
) -> List[int]:
    num_points = len(points)
    if num_points < 2:
        return []

    # Fix starting point at index 0
    population = [
        [0] + random.sample(range(1, num_points), num_points - 1)
        for _ in range(population_size)
    ]

    for _ in range(generations):
        population.sort(key=lambda r: total_distance(r, points))
        next_gen = population[:10]  # elite selection

        while len(next_gen) < population_size:
            a, b = random.sample(population[:20], 2)
            cut1, cut2 = sorted(random.sample(range(1, num_points), 2))
            child = a[:cut1] + [x for x in b if x not in a[:cut1]]
            if len(child) == num_points:
                next_gen.append(child)

        # Mutation: swap two cities randomly (excluding start index 0)
        for route in next_gen[10:]:
            if random.random() < 0.2:
                i, j = random.sample(range(1, num_points), 2)
                route[i], route[j] = route[j], route[i]

        population = next_gen

    best = min(population, key=lambda r: total_distance(r, points))
    return best

def optimize_route(locations: List[Dict[str, float]]) -> Dict[str, Any]:
    """Return optimized route (list of dicts) and total distance (km)."""
    if not locations or len(locations) < 2:
        return {"route": locations, "total_distance": 0.0}

    best_order = genetic_algorithm(locations)
    optimized = [locations[i] for i in best_order]
    dist = total_distance(best_order, locations)

    return {"route": optimized, "total_distance": dist}
