#frontend/app.py
import streamlit as st
import requests
import json
import pandas as pd
import folium
from streamlit_folium import st_folium
import math

# ---------------------------------
# Page config
# ---------------------------------
st.set_page_config(page_title="TravelSafari", page_icon="🚗", layout="wide")

# ---------------------------------
# Backend URL
# ---------------------------------
BACKEND_URL = "http://localhost:8000"

# ---------------------------------
# Haversine (only for segment display)
# ---------------------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# ---------------------------------
# Session state
# ---------------------------------
if "all_locations" not in st.session_state:
    st.session_state.all_locations = []

if "optimized_route" not in st.session_state:
    st.session_state.optimized_route = None

if "total_distance" not in st.session_state:
    st.session_state.total_distance = 0.0

if "estimated_cost" not in st.session_state:
    st.session_state.estimated_cost = 0.0

# ---------------------------------
# UI
# ---------------------------------
st.title("🚗 TravelSafari")
st.markdown("Enter city names or click on the map to add locations.")

# ---------------------------------
# Add by city name (BACKEND GEOCODING)
# ---------------------------------
with st.form("city_form"):
    city_name = st.text_input("Enter City Name", placeholder="e.g., Delhi")
    add_by_name = st.form_submit_button("➕ Add by Name")

    if add_by_name and city_name:
        try:
            res = requests.post(
                f"{BACKEND_URL}/geocode",
                json={
                    "place": city_name
                    },
            )

            if not res.ok:
                st.error(res.text)
            else:
                data = res.json()
                lat, lng = data["lat"], data["lng"]

                if {"lat": lat, "lng": lng} not in st.session_state.all_locations:
                    st.session_state.all_locations.append({"lat": lat, "lng": lng})
                    st.success(f"✅ {city_name} added: {lat:.4f}, {lng:.4f}")
                else:
                    st.warning("❗ Location already added.")

        except Exception as e:
            st.error(f"⚠️ Geocoding error: {e}")

# ---------------------------------
# Add by map click
# ---------------------------------
st.markdown("### 🗺️ Add by Clicking on Map")

m = folium.Map(location=[20, 78], zoom_start=5)
m.add_child(folium.LatLngPopup())
map_data = st_folium(m, width=700, height=400)

if map_data and map_data.get("last_clicked"):
    lat = map_data["last_clicked"]["lat"]
    lng = map_data["last_clicked"]["lng"]
    st.write(f"Clicked location: {lat:.6f}, {lng:.6f}")

    if st.button("➕ Add Clicked Location"):
        if {"lat": lat, "lng": lng} not in st.session_state.all_locations:
            st.session_state.all_locations.append({"lat": lat, "lng": lng})
            st.success("✅ Location added.")
        else:
            st.warning("❗ Location already added.")

# ---------------------------------
# Show added locations
# ---------------------------------
if st.session_state.all_locations:
    st.markdown("### 📍 Added Locations")
    for i, loc in enumerate(st.session_state.all_locations, 1):
        st.write(f"{i}. Lat: {loc['lat']}, Lng: {loc['lng']}")

    col1, col2 = st.columns([3, 1])

    # ---------------------------------
    # Optimize route
    # ---------------------------------
    with col1:
        if st.button("🧮 Optimize Route"):
            with st.spinner("Optimizing route..."):
                try:
                    res = requests.post(
                        f"{BACKEND_URL}/optimize",
                        json={"locations": st.session_state.all_locations},
                    )

                    if not res.ok:
                        st.error(res.text)
                    else:
                        data = res.json()
                        st.session_state.optimized_route = data["route"]
                        st.session_state.total_distance = data["total_distance"]
                        st.session_state.estimated_cost = data.get("estimated_cost",0.0)
                        st.success("✅ Route optimized!")

                except Exception as e:
                    st.error(f"⚠️ Optimization error: {e}")

    # ---------------------------------
    # Clear
    # ---------------------------------
    with col2:
        if st.button("🗑️ Clear All"):
            st.session_state.all_locations.clear()
            st.session_state.optimized_route = None
            st.session_state.total_distance = 0.0
            st.session_state.estimated_cost = 0.0
            st.info("🧹 Cleared.")

# ---------------------------------
# Display optimized route
# ---------------------------------
if st.session_state.optimized_route:
    st.markdown("### ✅ Optimized Route")

    df = pd.DataFrame(st.session_state.optimized_route).rename(columns={"lng": "lon"})

    st.markdown(f"### 📏 Total Distance: **{st.session_state.total_distance:.2f} km**")
    st.markdown(f"### 💰 Estimated Cost: **₹{st.session_state.estimated_cost:.2f}**")

    # Segment distances (display only)
    st.markdown("### 📍 Segment Distances")
    for i in range(len(df) - 1):
        d = haversine(
            df.loc[i, "lat"],
            df.loc[i, "lon"],
            df.loc[i + 1, "lat"],
            df.loc[i + 1, "lon"],
        )
        st.write(f"{i+1}. {d:.2f} km")

    # Map
    st.markdown("### 🗺️ Route Map")
    fmap = folium.Map(
        location=[df["lat"].mean(), df["lon"].mean()],
        zoom_start=5,
    )

    for i, row in df.iterrows():
        folium.Marker([row["lat"], row["lon"]], tooltip=f"Stop {i+1}").add_to(fmap)

    folium.PolyLine(
        df[["lat", "lon"]].values.tolist(),
        weight=4,
        opacity=0.8,
    ).add_to(fmap)

    st_folium(fmap, width=700, height=450)

    # ---------------------------------
    # Save route
    # ---------------------------------
    route_name = st.text_input("📝 Enter Route Name", placeholder="e.g., Golden Triangle")

    if st.button("💾 Save Route"):
        if not route_name.strip():
            st.warning("❗ Please enter a route name.")
        else:
            try:
                res = requests.post(
                f"{BACKEND_URL}/trips/",
                json={
                    "name": route_name.strip(),
                    "route": st.session_state.optimized_route,
                    "total_distance": round(st.session_state.total_distance, 2),
                    "estimated_cost": round(st.session_state.estimated_cost, 2),
                    },
                )
                
                if res.ok:
                    data = res.json()
                    if data.get("success"):
                        st.success("✅ Route saved successfully!")
                    else:
                        st.error(f"❌ Failed to save route: {data.get('message')}")
                else:
                    st.error(f"❌ Failed to save route: {res.text}")
                
            except Exception as e:
                    st.error(f"⚠️ Error saving route: {e}")

    # Downloads
    st.download_button(
        "📥 Download CSV",
        df.to_csv(index=False).encode("utf-8"),
        "optimized_route.csv",
        "text/csv",
    )

    st.download_button(
        "📥 Download JSON",
        json.dumps({"route": st.session_state.optimized_route}, indent=2).encode("utf-8"),
        "optimized_route.json",
        "application/json",
    )

# ---------------------------------
# View saved routes
# ---------------------------------
with st.expander("📚 View All Saved Routes"):
    if st.button("🔄 Refresh List"):
        res = requests.get(f"{BACKEND_URL}/get_routes")
        if res.ok:
            routes = res.json().get("routes", [])
            if not routes:
                st.info("No saved routes.")
            for i, r in enumerate(routes, 1):
                st.markdown(
                    f"**{i}. {r['name']}** — {r['total_distance']:.2f} km | ₹{r['estimated_cost']:.2f}"
                )
        else:
            st.error("Failed to fetch routes.")
