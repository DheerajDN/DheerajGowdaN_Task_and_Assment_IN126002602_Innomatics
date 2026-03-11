from fastapi import FastAPI, Query
app = FastAPI()
 
# ── Temporary data — acting as our database for now ──────────
products = [
    {'id': 1, 'name': 'Wireless Mouse', 'price': 499,  'category': 'Electronics', 'in_stock': True },
    {'id': 2, 'name': 'Notebook', 'price':  99,  'category': 'Stationery',  'in_stock': True },
    {'id': 3, 'name': 'USB Hub', 'price': 799, 'category': 'Electronics', 'in_stock': False},
    {'id': 4, 'name': 'Pen Set', 'price':  49, 'category': 'Stationery',  'in_stock': True },
    {'id': 5, 'name': 'Laptop Stand', 'price': 1499, 'category': 'Electronics', 'in_stock': True},
    {'id': 6, 'name': 'Mechanical Keyboard', 'price': 11999, 'category': 'Electronics', 'in_stock': True},
    {'id': 7, 'name': 'Webcam', 'price': 2499, 'category': 'Electronics', 'in_stock': False},
]
 
# ── Endpoint 0 — Home ────────────────────────────────────────
@app.get('/')
def home():
    return {'message': 'Welcome to our E-commerce API'}
 
# ── Endpoint 1 — Return all products ──────────────────────────
@app.get('/products')
def get_all_products():
    return {'products': products, 'total': len(products)}

@app.get('/products/summary')
def get_products_summary():
    total_products = len(products)
    in_stock_count = sum(1 for p in products if p.get("in_stock"))
    out_of_stock_count = total_products - in_stock_count
    raw_expensive = max(products, key=lambda p: p["price"])
    raw_cheapest = min(products, key=lambda p: p["price"])
    most_expensive = {"name": raw_expensive["name"], "price": raw_expensive["price"]}
    cheapest = {"name": raw_cheapest["name"], "price": raw_cheapest["price"]}
    categories = list({p["category"] for p in products})

    return {
        "total_products": total_products,
        "in_stock_count": in_stock_count,
        "out_of_stock_count": out_of_stock_count,
        "most_expensive": most_expensive,
        "cheapest": cheapest,
        "categories": categories
    }

@app.get('/products/filter')
def filter_products(
    category:  str  = Query(None, description='Electronics or Stationery'),
    min_price: int  = Query(None, description='Minimum price'),
    max_price: int  = Query(None, description='Maximum price'),
    in_stock:  bool = Query(None, description='True = in stock only')
):
    result = products          # start with all products
 
    if category:
        result = [p for p in result if p['category'] == category]
    
    if min_price is not None:
        result = [p for p in result if p['price'] >= min_price]
 
    if max_price:
        result = [p for p in result if p['price'] <= max_price]
 
    if in_stock is not None:
        result = [p for p in result if p['in_stock'] == in_stock]
 
    return {'filtered_products': result, 'count': len(result)}

# ----- EndPoint 2 -- Returns only available products -----
@app.get("/products/instock")
def get_instock_products():
    in_stock_products = [p for p in products if p.get("in_stock") is True]
    return {
        "in_stock_products": in_stock_products, 
        "count": len(in_stock_products)
        }

# ----- EndPoint 3 -- Compare products to find best deal and premium pick -----
@app.get("/products/deals")
def get_product_deals():
    best_deal=min(products, key=lambda p: p["price"])
    premium_pick=max(products, key=lambda p: p["price"])
    return {
        "best_deal": best_deal,
        "premium_pick": premium_pick
    }
 
# ── Endpoint 4 — Return one product by its ID ──────────────────
@app.get('/products/{product_id}')
def get_product(product_id: int):
    for product in products:
        if product['id'] == product_id:
            return {'product': product}
    return {'error': 'Product not found'}

# ----- EndPoint 5 -- Get specific product price details -----
@app.get('/products/{product_id}/price')
def get_product_price(product_id: int):
    for product in products:
        if product['id'] == product_id:
            return {
                "name": product["name"],
                "price": product["price"]
            }
    return {"error": "Product not found"}

# ----- EndPoint 6 -- Filters Products by Category -----
@app.get('/products/category/{category_name}')
def get_products_by_category(category_name: str):
    filtered_products=[
        p for p in products if p["category"]==category_name
    ]
    
    if not filtered_products:
        return{"error": "No products found in this category"}        
    return filtered_products

# ----- EndPoint 7 -- Summary of the store -----
@app.get('/store/summary')
def get_store_summary():
    total_count=len(products)
    in_stock_count=sum(1 for p in products if p.get("in_stock") is True)
    out_of_stock_count=total_count - in_stock_count
    unique_categories=list({p.get("category") for p in products if "category" in p})
    return {
        "store_name": "My E-commerce Store",
        "total_products": total_count,
        "in_stock_count": in_stock_count,
        "out_of_stock_count": out_of_stock_count,
        "unique_categories": unique_categories
    }

# ----- EndPoint 8 -- Search products by keyword in name -----
@app.get("/products/search/{keyword}")
def search_products(keyword: str):
    search_term=keyword.lower()
    matched_products=[
        p for p in products 
        if search_term in p.get("name", "").lower()
    ]
    if not matched_products:
        return{"message": "No products matched your search"}
    return {
        "keyword": keyword,
        "total_matches": len(matched_products),
        "products": matched_products
    }

from pydantic import BaseModel, Field
from typing import Optional

class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=100)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)
feedback_db = []

@app.post("/feedback")
def create_feedback(feedback: CustomerFeedback):
    new_feedback = feedback.dict()
    feedback_db.append(new_feedback)
    
    return {
        "message": "Feedback received! Thank you.",
        "saved_feedback": new_feedback,
        "total_feedback_count": len(feedback_db)
    }

from pydantic import BaseModel, Field, EmailStr 
from typing import List

class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1, le=50)

class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str = Field(..., min_length=5)
    items: List[OrderItem] = Field(..., min_items=1)

orders_db = []
@app.post("/orders")
def create_order(order: BulkOrder):
    new_id = len(orders_db) + 1
    order_data = {
        "order_id": new_id,
        "company": order.company_name,
        "status": "pending", 
        "items": order.items
    }
    orders_db.append(order_data)
    return order_data
@app.get("/orders/{order_id}")
def get_order(order_id: int):
    order = next((o for o in orders_db if o["order_id"] == order_id), None)
    if not order:
        return {"error": "Order not found"} 
    return order

@app.post("/orders/bulk")
def process_bulk_order(order: BulkOrder):
    processed_items = []
    failed_items = []
    grand_total = 0
    for item in order.items:
        product = next((p for p in products if p["id"] == item.product_id), None)
        if not product:
            failed_items.append({"product_id": item.product_id, "reason": "Product not found"})
            continue
        if not product["in_stock"]:
            failed_items.append({"product_id": item.product_id, "name": product["name"], "reason": "Out of stock"})
            continue
        item_total = product["price"] * item.quantity
        grand_total += item_total    
        processed_items.append({
            "product_id": item.product_id,
            "name": product["name"],
            "quantity": item.quantity,
            "subtotal": item_total
        })
    return {
        "company": order.company_name,
        "status": "Partial Success" if failed_items else "Success",
        "summary": {
            "total_processed": len(processed_items),
            "total_failed": len(failed_items),
            "grand_total": grand_total
        },
        "processed_items": processed_items,
        "failed_items": failed_items
    }

@app.patch("/orders/{order_id}/confirm")
def confirm_order(order_id: int):
    order = next((o for o in orders_db if o["order_id"] == order_id), None)
    if not order:
        return {"error": "Order not found"}
    order["status"] = "confirmed"
    return {
        "message": f"Order {order_id} has been confirmed.",
        "order": order
    }