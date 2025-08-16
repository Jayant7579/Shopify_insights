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
