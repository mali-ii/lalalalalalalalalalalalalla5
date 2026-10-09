"""Функции каталога и заказов для учебного проекта «СпортТовары»."""

import json
from pathlib import Path
from typing import Any
from collections.abc import Iterable


def _total_stock(product: dict[str, Any]) -> int:
    """Возвращает остаток с учётом вариантов представления товара."""
    if "stocks" in product:
        stocks = product["stocks"]
        if isinstance(stocks, dict):
            return sum(int(value) for value in stocks.values())
        return sum(int(item.get("quantity", 0)) for item in stocks)
    if "sizes" in product and isinstance(product["sizes"], dict):
        return sum(int(value) for value in product["sizes"].values())
    return int(product.get("quantity", product.get("stock", 0)))


def get_low_stock(products: Iterable[dict[str, Any]], limit: int = 3) -> list[dict[str, Any]]:
    """Выбирает товары с суммарным остатком не выше limit, по возрастанию."""
    matches = [product for product in products if _total_stock(product) <= limit]
    return sorted(matches, key=lambda product: (_total_stock(product), str(product.get("name", "")).casefold()))


def search_advanced(
    products: Iterable[dict[str, Any]],
    query: str = "",
    category: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
) -> list[dict[str, Any]]:
    """Ищет по названию/бренду и одновременно применяет заданные фильтры."""
    if not query.strip():
        return []
    needle = query.casefold().strip()
    result = []
    for product in products:
        searchable = f"{product.get('name', '')} {product.get('brand', '')}".casefold()
        if needle not in searchable:
            continue
        if category is not None and str(product.get("category", "")).casefold() != category.casefold():
            continue
        price = float(product.get("price", 0))
        if min_price is not None and price < min_price:
            continue
        if max_price is not None and price > max_price:
            continue
        result.append(product)
    return result


def count_by_category(products: Iterable[dict[str, Any]]) -> dict[str, int]:
    """Подсчитывает число товарных записей в каждой категории."""
    counts: dict[str, int] = {}
    for product in products:
        category = str(product.get("category", "Без категории"))
        counts[category] = counts.get(category, 0) + 1
    return counts


def save_orders(orders: Any, filename: str | Path = "orders.json") -> None:
    """Сохраняет заказы в JSON с поддержкой кириллицы."""
    with Path(filename).open("w", encoding="utf-8") as file:
        json.dump(orders, file, ensure_ascii=False, indent=2)


def total_sum(products: Iterable[dict[str, Any]]) -> float:
    """Считает стоимость товара с учётом количества (по умолчанию 1)."""
    return sum(float(p.get("price", 0)) * int(p.get("quantity", 1)) for p in products)


def _find_product(products: Iterable[dict[str, Any]], product_id: Any) -> dict[str, Any] | None:
    return next((p for p in products if p.get("id") == product_id), None)


def _matching_cart_item(cart: list[dict[str, Any]], product_id: Any, size: Any = None) -> dict[str, Any] | None:
    return next((item for item in cart if item.get("id") == product_id and item.get("size") == size), None)


def add_to_cart(
    cart: list[dict[str, Any]], products: Iterable[dict[str, Any]],
    product_id: Any, size: Any = None, quantity: int = 1,
) -> tuple[bool, str]:
    """Добавляет товар в корзину; для размерного товара проверяет размер и остаток."""
    product = _find_product(products, product_id)
    if product is None:
        return False, "Товар не найден"
    if quantity <= 0:
        return False, "Количество должно быть положительным"

    sizes = product.get("sizes")
    if sizes is not None:
        if not isinstance(sizes, dict):
            return False, "Некорректные данные о размерах"
        size_key = next((key for key in sizes if str(key) == str(size)), None)
        if size_key is None:
            return False, "Такого размера нет у товара"
        stock = int(sizes[size_key])
        size = size_key
    else:
        stock = _total_stock(product)

    current = _matching_cart_item(cart, product_id, size)
    already_in_cart = int(current.get("quantity", 0)) if current else 0
    if already_in_cart + quantity > stock:
        return False, "Недостаточно товара в наличии"
    if current:
        current["quantity"] = already_in_cart + quantity
    else:
        cart.append({
            "id": product_id,
            "name": product.get("name", ""),
            "size": size,
            "price": float(product.get("price", 0)),
            "quantity": quantity,
        })
    return True, "Товар добавлен в корзину"


def remove_from_cart(cart: list[dict[str, Any]], product_id: Any, size: Any = None) -> bool:
    """Удаляет позицию по id и размеру; возвращает True, если позиция найдена."""
    item = _matching_cart_item(cart, product_id, size)
    if item is None:
        return False
    cart.remove(item)
    return True


def update_quantity(cart: list[dict[str, Any]], product_id: Any, size: Any, quantity: int) -> bool:
    """Изменяет количество позиции; нулевое и отрицательное количество отклоняется."""
    item = _matching_cart_item(cart, product_id, size)
    if item is None or quantity <= 0:
        return False
    item["quantity"] = quantity
    return True


def cart_total(cart: Iterable[dict[str, Any]]) -> float:
    """Возвращает сумму корзины с учётом количества каждой позиции."""
    return sum(float(item.get("price", 0)) * int(item.get("quantity", 1)) for item in cart)
