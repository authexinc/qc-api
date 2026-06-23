import os
import time
import datetime as dt
from zoneinfo import ZoneInfo
from dotenv import load_dotenv, set_key
from requests import post
from sqlalchemy import select

from . import quantconnect as qc
from db.model import Session, Order
from db import update_row as ur

load_dotenv()


def update_algo_id() -> str:
    """
    Pulls the latest running deploy ID (algorithmId) from the QuantConnect list endpoint,
    sets it in the environment and matches/updates the ALGO_ID in the .env file.
    """
    path = '.env'
    project_id = os.getenv('PROJECT_ID')
    if not project_id:
        return os.getenv('ALGO_ID')

    payload = {
        "projectId": project_id,
        "status": "Running"
    }

    try:
        response = post(f"{qc.BASE_URL}/live/list", headers=qc.get_headers(), json=payload)
        response.raise_for_status()
        data = response.json()
        if data.get('live'):
            latest_id = data['live'][0]['deployId']
            current_id = os.getenv('ALGO_ID')
            if latest_id != current_id:
                set_key(path, 'ALGO_ID', latest_id)
                os.environ['ALGO_ID'] = latest_id
            return latest_id
    except Exception:
        pass

    return os.getenv('ALGO_ID')


def parse_time(time_str: str) -> dt.datetime:
    """
    Parses the order ISO 8601 time string (which is in UTC as indicated by 'Z'),
    converts it to US/Eastern timezone, and returns it as a naive datetime.
    """
    if not time_str:
        return None
    parsed_dt = dt.datetime.fromisoformat(time_str)
    if parsed_dt.tzinfo is not None:
        parsed_dt = parsed_dt.astimezone(ZoneInfo("US/Eastern"))
    return parsed_dt.replace(tzinfo=None)


def fetch_orders(algo_id: str) -> list:
    """
    Fetches all orders from the QuantConnect live orders endpoint using pagination.
    """
    def request(start=0, end=1) -> dict:
        payload = {
            'algorithmId': algo_id,
            "start": start,
            'end': end,
            'projectId': os.getenv('PROJECT_ID')
        }
        response = post(f"{qc.BASE_URL}/live/orders/read",
                        headers=qc.get_headers(), json=payload)
        response.raise_for_status()
        return response.json()

    initial_res = request(0, 1)
    while initial_res.get('status') == 'loading':
        time.sleep(5)
        initial_res = request(0, 1)
        
    total_length = initial_res.get('length', 0)
    
    orders = []
    chunk_size = 1000
    for start_idx in range(0, total_length, chunk_size):
        end_idx = min(start_idx + chunk_size, total_length)
        chunk_res = request(start_idx, end_idx)
        if chunk_res and 'orders' in chunk_res:
            orders.extend(chunk_res['orders'])
            
    return orders


def process_and_save_orders(orders_list: list, algo_id: str) -> int:
    """
    Extracts ID, price, time, symbol from orders list, parses time,
    sorts from oldest to newest, checks for duplicates, and appends to the database.
    Returns the number of new orders inserted.
    """
    parsed_orders = []
    
    for order in orders_list:
        order_id = order.get('id')
        price = order.get('price')
        time_str = order.get('lastFillTime') or order.get('time')
        symbol = order.get('symbol', {}).get('value') if isinstance(order.get('symbol'), dict) else order.get('symbol')
        
        if order_id is None or not time_str:
            continue
            
        order_algo_id = algo_id
        if order.get('events'):
            order_algo_id = order.get('events')[0].get('algorithmId') or algo_id
            
        exact_time = parse_time(time_str)
        linked_time = exact_time.replace(second=0, microsecond=0)
        
        parsed_orders.append({
            'order_id': order_id,
            'price': price,
            'time': exact_time,
            'symbol': symbol,
            'algo_id': order_algo_id,
            'datetime': linked_time
        })
        
    # Sort orders from oldest to newest
    parsed_orders.sort(key=lambda x: x['time'])
    
    session = Session()
    new_inserted_count = 0
    
    for o in parsed_orders:
        # Check for duplicates by order_id and algo_id
        existing = session.execute(
            select(Order).where(
                Order.order_id == o['order_id'],
                Order.algo_id == o['algo_id']
            )
        ).scalar_one_or_none()
        
        if existing:
            continue
            
        try:
            ur.populate_order(
                order_id_=o['order_id'],
                price_=o['price'],
                time_=o['time'],
                symbol_=o['symbol'],
                algo_id_=o['algo_id'],
                datetime_=o['datetime']
            )
            new_inserted_count += 1
        except Exception:
            pass
            
    session.close()
    return new_inserted_count


def add_orders_to_db() -> int:
    """
    Wrapper function that performs the entire workflow of updating AlgoID,
    fetching live orders, and inserting them into the database.
    """
    algo_id = update_algo_id()
    if not algo_id:
        return 0
    orders = fetch_orders(algo_id)
    return process_and_save_orders(orders, algo_id)


if __name__ == "__main__":
    # Ensure DB tables are created
    from db.model import Base, engine
    Base.metadata.create_all(engine)
    inserted = add_orders_to_db()
    print(f"Added {inserted} new orders to DB.")
