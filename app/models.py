from pydantic import BaseModel, Field
from typing import List, Optional

class Product(BaseModel):
    id: Optional[int] = None
    title: Optional[str] = None
    handle: Optional[str] = None
    body_html: Optional[str] = None
    vendor: Optional[str] = None
    product_type: Optional[str] = None
    tags: Optional[str] = None
    url: Optional[str] = None

class FAQ(BaseModel):
    question: str = Field(...)
    answer: str = Field(...)

class ContactDetails(BaseModel):
    emails: List[str] = []
    phones: List[str] = []
    addresses: List[str] = []

class PolicyLink(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None
    text_excerpt: Optional[str] = None

class BrandResponse(BaseModel):
    website_url: str
    is_shopify_like: bool = False
    product_catalog: List[Product] = []
    hero_products: List[Product] = []
    privacy_policy: Optional[PolicyLink] = None
    return_refund_policy: Optional[PolicyLink] = None
    faqs: List[FAQ] = []
    social_handles: List[str] = []
    contact_details: ContactDetails = ContactDetails()
    about_brand: Optional[str] = None
    important_links: List[str] = []
    fetched_at: Optional[str] = None
    errors: List[str] = []
