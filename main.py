import json
import random
import time
import requests
from rich import print

with open("config.json", encoding="utf-8") as f:
    config = json.load(f)

session = requests.Session()
session.cookies.update({"_RoliVerification": config.get("roli_verification")})

player_id = int(config.get("player_id"))

# Replace these with four valid item IDs from your inventory
offer_items = [1609401184, 16477149823, 16477149823, 1048037]  # Example IDs; replace with valid ones
request_items = []  # Keep this as a valid ID, or set to [] if not requesting specific items
request_tags = ["upgrade", "downgrade"]  # Set to both tags as requested

def post_ad(item_ids: list[int], request_ids: list[int], tags: list[str]) -> None:
    combined_tags = tags if tags else []
    
    payload = {
        "player_id": player_id,
        "offer_item_ids": item_ids,
        "request_item_ids": request_ids,
        "request_tags": combined_tags
    }
    print(f"Sending payload: {json.dumps(payload, indent=2)}")
    
    try:
        req = session.post("https://api.rolimons.com/tradeads/v1/createad", json=payload)
        res = req.json()
        print(f"Response: {json.dumps(res, indent=2)}")
    except ValueError as e:
        print(f"[bold red]ERROR[/] Failed to parse API response: {e}")
        return
    
    if res.get("success", False):
        print(f"[bold green]SUCCESS[/] Ad posted {item_ids} - Requested: {request_ids if request_ids else 'None'} - Tags: {combined_tags}")
        return

    print(f'[bold red]ERROR[/] Couldn\'t post ad (Reason: {res.get("message", "Unknown error")}) - Check item IDs: {item_ids + request_ids}')

while True:
    post_ad(offer_items, request_items, request_tags)

    random_time = random.randint(15, 15)
    print(f"Waiting {random_time} minutes before attempting to post another ad")
    time.sleep(random_time * 60)
