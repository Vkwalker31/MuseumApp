"""
Сессионная корзина заказа для услуг (TicketPrice).
Ключ сессии: 'cart' → {service_id: quantity}.
"""
from decimal import Decimal

from .models import TicketPrice

CART_SESSION_KEY = 'cart'


def get_cart(session):
    return session.get(CART_SESSION_KEY, {})


def save_cart(session, cart):
    session[CART_SESSION_KEY] = cart
    session.modified = True


def add_to_cart(session, service_id, quantity=1):
    cart = get_cart(session)
    key = str(service_id)
    cart[key] = cart.get(key, 0) + max(1, int(quantity))
    save_cart(session, cart)


def set_quantity(session, service_id, quantity):
    cart = get_cart(session)
    key = str(service_id)
    quantity = int(quantity)
    if quantity <= 0:
        cart.pop(key, None)
    else:
        cart[key] = quantity
    save_cart(session, cart)


def remove_from_cart(session, service_id):
    cart = get_cart(session)
    cart.pop(str(service_id), None)
    save_cart(session, cart)


def clear_cart(session):
    save_cart(session, {})


def cart_items(session):
    """Список позиций корзины с объектами услуг и суммами."""
    cart = get_cart(session)
    items = []
    total = Decimal('0.00')
    ids = [int(k) for k in cart.keys() if str(k).isdigit()]
    services = {s.pk: s for s in TicketPrice.objects.filter(pk__in=ids)}
    for sid, qty in cart.items():
        service = services.get(int(sid))
        if not service:
            continue
        qty = int(qty)
        line_total = service.base_price * qty
        total += line_total
        items.append({
            'service': service,
            'quantity': qty,
            'line_total': line_total,
        })
    return items, total


def cart_count(session):
    return sum(int(q) for q in get_cart(session).values())
