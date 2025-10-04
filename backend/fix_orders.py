"""
Script to fix existing orders with $0.00 total
Save this as backend/fix_orders.py and run it once
"""

from app import create_app
from database import db
from models.order import Order
from decimal import Decimal


def fix_order_totals():
    app = create_app()

    with app.app_context():
        # Get all orders with 0 or null total_amount
        orders = Order.query.filter(
            db.or_(Order.total_amount == 0, Order.total_amount == None)
        ).all()

        print(f"Found {len(orders)} orders with $0.00 total")

        for order in orders:
            # Calculate subtotal from order items
            subtotal = sum(item.total_price for item in order.order_items)

            # Calculate tax (8%)
            tax_amount = subtotal * Decimal("0.08")

            # Calculate shipping
            shipping_cost = Decimal("0.00") if subtotal >= 50 else Decimal("5.99")

            # Calculate total
            total_amount = subtotal + tax_amount + shipping_cost

            # Update order
            order.total_amount = total_amount

            print(
                f"Order {order.order_number}: ${subtotal} + ${tax_amount} + ${shipping_cost} = ${total_amount}"
            )

        # Commit changes
        db.session.commit()
        print(f"\n✅ Fixed {len(orders)} orders!")


if __name__ == "__main__":
    fix_order_totals()
