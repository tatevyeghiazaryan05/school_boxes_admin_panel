from datetime import date

from fastapi import APIRouter, Depends, HTTPException

import main
from security import get_current_admin


admin_orders_router = APIRouter(prefix="/adminpanel", tags=["admin_order_service"])


@admin_orders_router.get("/api/admin/get/orders/by/id/{order_id}")
def get_order_by_id(order_id: int,token=Depends(get_current_admin)):
    try:
        main.cursor.execute("SELECT * FROM orders WHERE id=%s",
                            (order_id,))
        order = main.cursor.fetchone()
        return order
    except Exception:
        raise HTTPException(status_code=500, detail="Server error while fetching order by ID")


@admin_orders_router.get("/api/admin/get/orders/by/date/{start_date}/{end_date}")
def get_order_by_date(start_date: date, end_date: date,token=Depends(get_current_admin)):
    try:
        main.cursor.execute("SELECT * FROM orders WHERE created_at >= %s AND created_at <= %s",
                        (start_date, end_date))
        orders = main.cursor.fetchall()
        return orders
    except Exception:
        raise HTTPException(status_code=500, detail="Server error while fetching orders by date")


@admin_orders_router.get("/api/admin/get/orders/by/price/{min_price}/{max_price}")
def get_order_by_date(min_price: float, max_price: float,token=Depends(get_current_admin)):
    try:
        main.cursor.execute("SELECT * FROM orders WHERE total_price >= %s AND total_price <= %s",
                        (min_price, max_price))
        orders = main.cursor.fetchall()
        return orders
    except Exception:
        raise HTTPException(status_code=500, detail="Server error while fetching orders by date")

