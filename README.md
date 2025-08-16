# Shopify Store Insights-Fetcher (Full Project)

A **FastAPI + React** project that fetches insights from Shopify stores **without using the official Shopify API**.  
It extracts structured brand data like products, policies, FAQs, contact info, and even fetches competitor store insights.  
Results can be persisted into **MySQL** (bonus).

---

## 🚀 Features
- ✅ Fetch **Shopify store insights** via `/fetch-insights`
- ✅ Extract:
  - Product catalog (via `/products.json`)
  - Hero products (homepage highlights)
  - Privacy & Return/Refund policies
  - FAQs (schema.org JSON-LD + heuristics)
  - Social handles (IG, FB, TikTok, Twitter, etc.)
  - Contact details (emails, phone numbers)
  - About text
  - Important links (blogs, contact, order tracking, shipping)
- ✅ **Competitor Analysis**: `/fetch-insights-with-competitors`
- ✅ **DB Persistence** into MySQL
- ✅ **React Frontend** demo UI

---

## 🛠️ Tech Stack
- **Backend:** Python, FastAPI, BeautifulSoup4, Requests, MySQL
- **Frontend:** React + Vite + Axios
- **DB (optional):** MySQL (local or Docker)

---

## 📂 Project Structure
shopify_insights_full/
│── app/ # FastAPI backend
│ ├── main.py # API routes
│ ├── scraper.py # Scraping + competitor logic
│ ├── models.py # Pydantic data models
│ ├── utils.py # Helper functions
│ ├── db.py # MySQL persistence
│── frontend/ # React frontend (Vite)
│ ├── src/
│ │ ├── App.jsx
│ │ ├── main.jsx
│ │ └── index.css
│ ├── package.json
│ └── index.html
│── tests/ # API smoke tests
│── requirements.txt # Backend dependencies
│── README.md

#### Install & Run
```bash
cd shopify_insights_full
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

 Fetch insights for a store
curl "http://127.0.0.1:8000/fetch-insights/?website_url=https://memy.co.in"

# Fetch insights with competitor analysis
curl "http://127.0.0.1:8000/fetch-insights-with-competitors/?website_url=https://memy.co.in"

cd frontend
npm install
npm run dev
App runs at → http://127.0.0.1:5173

Backend must be running on http://127.0.0.1:8000

3️⃣ MySQL Persistence (Bonus)
Run MySQL locally or via Docker:

bash
Copy
Edit
docker run --name shopifydb -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=shopify_insights -p 3306:3306 -d mysql:8
Set environment variables:

bash
Copy
Edit
export MYSQL_HOST=localhost
export MYSQL_USER=root
export MYSQL_PASSWORD=root
export MYSQL_DB=shopify_insights
When you fetch insights, data will be saved automatically into MySQL.
