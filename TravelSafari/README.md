# 🚗	TravelSafari

A full-stack web application that helps users plan efficient multi-stop travel routes. Enter city names or click on the map to add locations, then optimize the visiting order using a genetic algorithm. Visualize distances and paths interactively, save your routes to the server, or export them as CSV/JSON.

---

## 🔥 Features

- **Add Locations**
  - By city name (via OpenCage Geocoding API)
  - By clicking directly on an interactive map (Folium + Streamlit-Folium)
- **Route Optimization**
  - FastAPI backend implements a Genetic Algorithm (TSP) for route sequencing
  - Haversine distance calculations
- **Interactive Map**
  - PyDeck + OpenStreetMap to display scatter points & polylines
  - Real-time segment and total distance display
- **Persistence & Export**
  - Save optimized routes to server (JSON-lines file)
  - Download optimized routes as CSV or JSON
- **User-friendly UI**
  - Built with Streamlit for one-click deploy and instant feedback
  - Dark/light configuration, responsive layout

---

## 🚀 Tech Stack

- **Frontend**:  
  - [Streamlit](https://streamlit.io)  
  - [PyDeck](https://pydeck.gl) + OpenStreetMap  
  - [Folium](https://python-visualization.github.io/folium/) + [streamlit-folium](https://github.com/randyzwitch/streamlit-folium)  
  - [OpenCage Geocoding API](https://opencagedata.com/)
- **Backend**:  
  - [FastAPI](https://fastapi.tiangolo.com)  
  - Genetic Algorithm for TSP  
  - Haversine distance formula  
- **Persistence**:  
  - JSON-lines file (`saved_routes.jsonl`)  
  - (easily replaceable with any database)

---

## 📦 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/travel-route-optimizer.git
cd travel-route-optimizer
```

### 2. Create & activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure your API Keys
Create a `.env` file in the `backend/` directory:
```ini
OPENCAGE_API_KEY=your_opencage_key_here
```

### 5. Run the backend
```bash
cd backend
uvicorn main:app --reload
```

### 6. Run the frontend
In a new terminal:
```bash
cd frontend
streamlit run app.py
```

Open your browser to `http://localhost:8501` to use the app.

---

## 🛠 Usage

1. **Add Locations**  
   - Type a city name and click **➕ Add Location**, or click on the map to pick a point.
2. **Optimize Route**  
   - Click **🧮 Optimize Route** to compute the best visiting order.
3. **View Distances**  
   - Segment distances and total route distance appear above the map.
4. **Save / Export**  
   - **💾 Save Route to Server** stores the route in `backend/saved_routes.jsonl`.  
   - **📥 Download CSV/JSON** lets you export the route for offline use.
5. **Clear**  
   - Click **🗑️ Clear All Locations** to reset and start over.

---

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request with improvements, bug fixes, or new features.

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---
```

Feel free to copy this into your repo’s **README.md**, update URLs/badges, and then commit & push to GitHub:  
```bash
git add README.md
git commit -m "Add project description"
git push
```