import sqlite3
import random
from pathlib import Path
from datetime import datetime, timedelta

DB_PATH = Path("data/vkusvill_demo.db")

random.seed(42)


def random_date(start: datetime, end: datetime) -> datetime:
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.executescript("""
    PRAGMA foreign_keys = ON;

    CREATE TABLE customers (
        customer_id INTEGER PRIMARY KEY,
        registration_date TEXT NOT NULL,
        city TEXT NOT NULL,
        gender TEXT,
        birth_year INTEGER,
        loyalty_level TEXT NOT NULL
    );

    CREATE TABLE stores (
        store_id INTEGER PRIMARY KEY,
        city TEXT NOT NULL,
        store_format TEXT NOT NULL,
        opened_date TEXT NOT NULL
    );

    CREATE TABLE categories (
        category_id INTEGER PRIMARY KEY,
        category_name TEXT NOT NULL
    );

    CREATE TABLE products (
        product_id INTEGER PRIMARY KEY,
        product_name TEXT NOT NULL,
        category_id INTEGER NOT NULL,
        is_private_label INTEGER NOT NULL,
        base_price REAL NOT NULL,
        FOREIGN KEY (category_id) REFERENCES categories(category_id)
    );

    CREATE TABLE orders (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER NOT NULL,
        store_id INTEGER,
        order_date TEXT NOT NULL,
        channel TEXT NOT NULL,
        status TEXT NOT NULL,
        delivery_minutes INTEGER,
        promo_flag INTEGER NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
        FOREIGN KEY (store_id) REFERENCES stores(store_id)
    );

    CREATE TABLE order_items (
        order_item_id INTEGER PRIMARY KEY,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        discount_amount REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(order_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    );
    """)

    cities = ["Москва", "Санкт-Петербург", "Казань", "Нижний Новгород", "Екатеринбург"]
    loyalty_levels = ["base", "silver", "gold"]
    genders = ["M", "F", None]

    categories = [
        "Молочные продукты",
        "Овощи и фрукты",
        "Готовая еда",
        "Мясо и птица",
        "Рыба",
        "Хлеб и выпечка",
        "Напитки",
        "Сладости",
    ]

    products_by_category = {
        "Молочные продукты": ["Молоко", "Творог", "Йогурт", "Кефир"],
        "Овощи и фрукты": ["Яблоки", "Бананы", "Огурцы", "Томаты"],
        "Готовая еда": ["Салат", "Суп", "Паста", "Котлета"],
        "Мясо и птица": ["Куриное филе", "Фарш", "Индейка", "Говядина"],
        "Рыба": ["Лосось", "Треска", "Сельдь", "Креветки"],
        "Хлеб и выпечка": ["Хлеб", "Булочка", "Круассан", "Лаваш"],
        "Напитки": ["Вода", "Сок", "Морс", "Чай"],
        "Сладости": ["Шоколад", "Печенье", "Мармелад", "Зефир"],
    }

    for i, name in enumerate(categories, start=1):
        cur.execute(
            "INSERT INTO categories(category_id, category_name) VALUES (?, ?)",
            (i, name),
        )

    product_id = 1
    for category_id, category_name in enumerate(categories, start=1):
        for product_name in products_by_category[category_name]:
            base_price = round(random.uniform(60, 650), 2)
            is_private_label = random.choices([0, 1], weights=[0.35, 0.65])[0]

            cur.execute("""
                INSERT INTO products(
                    product_id, product_name, category_id, is_private_label, base_price
                )
                VALUES (?, ?, ?, ?, ?)
            """, (product_id, product_name, category_id, is_private_label, base_price))

            product_id += 1

    for store_id in range(1, 31):
        city = random.choice(cities)
        store_format = random.choice(["mini", "standard", "darkstore"])
        opened_date = random_date(datetime(2020, 1, 1), datetime(2024, 12, 31))

        cur.execute("""
            INSERT INTO stores(store_id, city, store_format, opened_date)
            VALUES (?, ?, ?, ?)
        """, (store_id, city, store_format, opened_date.date().isoformat()))

    for customer_id in range(1, 2001):
        registration_date = random_date(datetime(2022, 1, 1), datetime(2025, 12, 31))
        city = random.choice(cities)
        gender = random.choice(genders)
        birth_year = random.randint(1960, 2006)
        loyalty_level = random.choices(loyalty_levels, weights=[0.55, 0.30, 0.15])[0]

        cur.execute("""
            INSERT INTO customers(
                customer_id, registration_date, city, gender, birth_year, loyalty_level
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            customer_id,
            registration_date.date().isoformat(),
            city,
            gender,
            birth_year,
            loyalty_level,
        ))

    order_item_id = 1
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 12, 31)

    for order_id in range(1, 15001):
        customer_id = random.randint(1, 2000)
        order_date = random_date(start_date, end_date)

        channel = random.choices(
            ["offline", "delivery", "pickup"],
            weights=[0.55, 0.35, 0.10],
        )[0]

        store_id = random.randint(1, 30)
        status = random.choices(
            ["completed", "cancelled"],
            weights=[0.93, 0.07],
        )[0]

        delivery_minutes = None
        if channel == "delivery":
            delivery_minutes = max(10, int(random.gauss(47, 15)))

        promo_flag = random.choices([0, 1], weights=[0.7, 0.3])[0]

        cur.execute("""
            INSERT INTO orders(
                order_id, customer_id, store_id, order_date, channel,
                status, delivery_minutes, promo_flag
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            order_id,
            customer_id,
            store_id,
            order_date.date().isoformat(),
            channel,
            status,
            delivery_minutes,
            promo_flag,
        ))

        items_count = random.randint(1, 8)

        for _ in range(items_count):
            product_id = random.randint(1, 32)
            quantity = random.choices([1, 2, 3, 4], weights=[0.55, 0.25, 0.15, 0.05])[0]

            cur.execute(
                "SELECT base_price FROM products WHERE product_id = ?",
                (product_id,),
            )
            base_price = cur.fetchone()[0]

            price = round(base_price * random.uniform(0.9, 1.15), 2)
            discount_amount = 0.0

            if promo_flag:
                discount_amount = round(price * quantity * random.uniform(0.03, 0.20), 2)

            cur.execute("""
                INSERT INTO order_items(
                    order_item_id, order_id, product_id, quantity, price, discount_amount
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                order_item_id,
                order_id,
                product_id,
                quantity,
                price,
                discount_amount,
            ))

            order_item_id += 1

    conn.commit()
    conn.close()

    print(f"База создана: {DB_PATH}")


if __name__ == "__main__":
    init_db()