# SmartRouteAPI 🚦🗺️

**SmartRouteAPI** is an open-source project built with **FastAPI + PostgreSQL + PostGIS + pgRouting** for precise and fast route calculation between two points on a map.  
Developed by [Hossam Hassan]

---

## 🚀 What is SmartRouteAPI?

- 🔍 Calculates the shortest route between two points using **Dijkstra’s Algorithm**.
- 📡 Returns route data in **GeoJSON** format.
- 🛣️ Includes street names, distance, and estimated travel time.
- ⚡ Designed for speed and efficiency with geographic databases.

---

## 🗂️ Tech Stack

- **Backend:** FastAPI
- **Database:** PostgreSQL + PostGIS + pgRouting
- **Client:** Any app that can consume REST APIs (Web, Mobile, etc.)

---

## ⚙️ How to Run

```bash

# 2️⃣ Install dependencies
pip install -r requirements.txt

# 3️⃣ Start the API server
uvicorn main:app --reload
