from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from .scraper import fetch_brand_data
from .models import BrandResponse

app = FastAPI(title="Shopify Insights-Fetcher", version="1.0.0")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "Welcome to Shopify Insights API. Visit /docs for Swagger UI."}




@app.get("/fetch-insights/", response_model=BrandResponse)
def fetch_insights(website_url: str = Query(..., description="Full URL of the Shopify store, e.g., https://memy.co.in")):
    data = fetch_brand_data(website_url)
    if data.errors and not data.is_shopify_like and not data.product_catalog:
        raise HTTPException(status_code=401, detail="Website not found or unreachable")
    if not data.is_shopify_like and len(data.product_catalog) == 0:
        raise HTTPException(status_code=401, detail="Website is not detected as a Shopify store")
    return JSONResponse(content=data.model_dump())
