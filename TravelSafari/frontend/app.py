#frontend/app.py

import streamlit as st
import requests, json
from opencage.geocoder import OpenCageGeocode
import pandas as pd
import folium
from streamlit_folium import st_folium
import math

# Page config
st.set_page_config(page_title="TravelSafari", page_icon="🚗", layout="wide")

# API & Backend
OPENCAGE_API_KEY = "45b3f677b64f45d6bdc827723d813f9a"
BACKEND_URL = "http://localhost:8000"
geocoder = OpenCageGeocode(OPENCAGE_API_KEY)

# Haversine function
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# Init session state
if "all_locations" not in st.session_state:
    st.session_state.all_locations = []
if "optimized_route" not in st.session_state:
    st.session_state.optimized_route = None

# Title
st.title("🚗 TravelSafari")
st.markdown("Enter city names or click on map to add locations.")

# Form to add by city name
with st.form("city_form"):
    city_name = st.text_input("Enter City Name", placeholder="e.g., Delhi")
    add_by_name = st.form_submit_button("➕ Add by Name")
    if add_by_name and city_name:
        try:
            results = geocoder.geocode(city_name)
            if results:
                lat = results[0]["geometry"]["lat"]
                lng = results[0]["geometry"]["lng"]
                if {"lat": lat, "lng": lng} not in st.session_state.all_locations:
                    st.session_state.all_locations.append({"lat": lat, "lng": lng})
                    st.success(f"✅ {city_name} added: {lat}, {lng}")
                else:
                    st.warning("❗ Location already added.")
            else:
                st.warning("❗ No coordinates found.")
        except Exception as e:
            st.error(f"⚠️ Geocoding error: {e}")

# Add by map click
st.markdown("### 🗺️ Add by Clicking on Map")
m = folium.Map(location=[20, 78], zoom_start=5)
m.add_child(folium.LatLngPopup())
map_data = st_folium(m, width=700, height=400)

if map_data and map_data.get("last_clicked"):
    lat, lng = map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"]
    st.write(f"Clicked location: {lat:.6f}, {lng:.6f}")
    if st.button("➕ Add Clicked Location"):
        if {"lat": lat, "lng": lng} not in st.session_state.all_locations:
            st.session_state.all_locations.append({"lat": lat, "lng": lng})
            st.success(f"✅ Location added: {lat:.6f}, {lng:.6f}")
        else:
            st.warning("❗ Location already added.")

# Show added locations
if st.session_state.all_locations:
    st.markdown("### 📍 Added Locations:")
    for i, loc in enumerate(st.session_state.all_locations, 1):
        st.write(f"{i}. Latitude: {loc['lat']}, Longitude: {loc['lng']}")

    col1, col2 = st.columns([3, 1])

    with col1:
        if st.button("🧮 Optimize Route"):
            with st.spinner("Optimizing..."):
                try:
                    res = requests.post(f"{BACKEND_URL}/optimize", json={"locations": st.session_state.all_locations})
                    if not res.ok:
                        st.error(f"API Error: {res.text}")
                        st.stop()
                    optimized = res.json().get("route", [])
                    if not optimized:
                        st.warning("⚠️ No route returned.")
                        st.stop()
                    st.session_state.optimized_route = optimized
                    st.success("✅ Route optimized!")

                except Exception as e:
                    st.error(f"⚠️ Optimization error: {e}")

    with col2:
        if st.button("🗑️ Clear All"):
            st.session_state.all_locations.clear()
            st.session_state.optimized_route = None
            st.info("🧹 All cleared.")

# Display Optimized Route
if st.session_state.optimized_route:
    st.markdown("### ✅ Optimized Route")
    df = pd.DataFrame(st.session_state.optimized_route).rename(columns={"lng": "lon"})

    # Distance calculation
    total_dist = 0.0
    st.markdown("### 📏 Segment Distances:")
    for i in range(len(df) - 1):
        lat1, lon1 = df.loc[i, "lat"], df.loc[i, "lon"]
        lat2, lon2 = df.loc[i + 1, "lat"], df.loc[i + 1, "lon"]
        d = haversine(lat1, lon1, lat2, lon2)
        total_dist += d
        st.write(f"{i + 1}. ({lat1:.2f}, {lon1:.2f}) → ({lat2:.2f}, {lon2:.2f}) = {d:.2f} km")
    st.markdown(f"### 🧮 Total Distance: **{total_dist:.2f} km**")

    # Map
    st.markdown("### 🗺️ Route Map")
    folium_map = folium.Map(location=[df["lat"].mean(), df["lon"].mean()], zoom_start=5)
    for i, row in df.iterrows():
        folium.Marker([row["lat"], row["lon"]], tooltip=f"Stop {i + 1}").add_to(folium_map)
    folium.PolyLine(df[["lat", "lon"]].values.tolist(), color="blue", weight=4.5, opacity=0.8).add_to(folium_map)
    st_folium(folium_map, width=700, height=450)

    # Save route
    route_name = st.text_input("📝 Enter Route Name", placeholder="e.g., Golden Triangle")
    if st.button("💾 Save Route"):
        if not route_name.strip():
            st.warning("❗ Please enter a name.")
        else:
            save_res = requests.post(
                f"{BACKEND_URL}/save_route",
                json={"route": st.session_state.optimized_route,
                      "route_name": route_name.strip(),
                      "total_distance":round(total_dist, 2)}
            )
            if save_res.ok and save_res.json().get("status") == "saved":
                st.success(f"✅ Route '{route_name}' saved.")
            else:
                st.error("❌ Save failed.")

    # Downloads
    csv = df.to_csv(index=False).encode("utf-8")
    json_bytes = json.dumps({"route": st.session_state.optimized_route}, indent=2).encode("utf-8")
    st.download_button("📥 Download CSV", csv, "optimized_route.csv", "text/csv")
    st.download_button("📥 Download JSON", json_bytes, "optimized_route.json", "application/json")

# View all saved routes
with st.expander("📚 View All Saved Routes"):
    if st.button("🔄 Refresh List"):
        try:
            res = requests.get(f"{BACKEND_URL}/get_routes")
            if res.ok:
                saved_routes = res.json().get("routes", [])
                if not saved_routes:
                    st.info("ℹ️ No saved routes found.")
                else:
                    for idx, route_entry in enumerate(saved_routes, 1):
                        name = route_entry.get("name", f"Route {idx}")
                        route = route_entry.get("route", [])
                        distance = route_entry.get("total_distance", None)
                        if distance:
                            st.markdown(f"**{idx}. {name}** — {distance:.2f} km ({len(route)} points)")
                        else:
                            st.markdown(f"**{idx}. {name}** ({len(route)} points)")
                        # Expand for coordinates
                        with st.expander("Show Coordinates"):
                            for point in route:
                                st.write(f"- Lat: {point['lat']}, Lon: {point['lng']}")
            else:
                st.error("⚠️ Failed to fetch routes.")
        except Exception as e:
            st.error(f"⚠️ Error: {e}")
