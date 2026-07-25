from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from database import db

router = APIRouter(
    prefix="/api/orders",
    tags=["Orders"]
)

class OrderItem(BaseModel):
    medicine_name: str
    pharmacy_name: str
    pharmacy_license: str
    price: float
    discount: float
    quantity: int

class OrderCreate(BaseModel):
    orderId: str
    date: str
    amount: float
    paymentStatus: str
    transactionId: str
    orderStatus: str
    items: List[OrderItem]
    deliveryAddress: str
    userEmail: str

class OrderStatusUpdate(BaseModel):
    orderStatus: str

@router.post("")
def create_order(order: OrderCreate):
    try:
        order_data = order.dict()
        db.Orders.insert_one(order_data)
        return {"status": "Success", "message": "Order created successfully"}
    except Exception as e:
        return {"status": "Error", "details": str(e)}

@router.get("")
def get_all_orders():
    try:
        orders = list(db.Orders.find())
        for o in orders:
            o["_id"] = str(o["_id"])
        return {"status": "Success", "data": orders}
    except Exception as e:
        return {"status": "Error", "details": str(e)}

@router.put("/{order_id}")
def update_order_status(order_id: str, payload: OrderStatusUpdate):
    try:
        res = db.Orders.update_one(
            {"orderId": order_id},
            {"$set": {"orderStatus": payload.orderStatus}}
        )
        if res.modified_count > 0 or res.matched_count > 0:
            return {"status": "Success", "message": "Order status updated successfully"}
        return {"status": "Error", "message": "Order not found"}
    except Exception as e:
        return {"status": "Error", "details": str(e)}

@router.get("/user/{email}")
def get_user_orders(email: str):
    try:
        orders = list(db.Orders.find({"userEmail": email}))
        for o in orders:
            o["_id"] = str(o["_id"])
        orders.reverse()
        return {"status": "Success", "data": orders}
    except Exception as e:
        return {"status": "Error", "details": str(e)}

