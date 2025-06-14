import json
import random
import time
import requests
from rich import print

def load_config():
    try:
        with open("config.json", encoding="utf-8") as f:
            config = json.load(f)
        return config
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"[bold red]ERROR[/] Failed to load config: {e}")
        raise

def initialize_session(verification_token):
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json",
    })
    session.cookies.update({"_RoliVerification": verification_token})
    return session

def post_ad(session, player_id, offer_items, request_items, request_tags, ad_number):
    payload = {
        "player_id": player_id,
        "offer_item_ids": offer_items,
        "request_item_ids": request_items,
        "request_tags": request_tags
    }
    
    print(f"\n[bold]Sending Trade Ad #{ad_number}:[/]")
    print(f"➤ Offering: {offer_items}")
    print(f"➤ Requesting: {request_items if request_items else 'Anything'} ({', '.join(request_tags) if request_tags else 'No tags'})")
    
    try:
        response = session.post(
            "https://api.rolimons.com/tradeads/v1/createad",
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        res = response.json()
    except (requests.RequestException, ValueError) as e:
        print(f"[bold red]ERROR[/] API request failed: {e}")
        return False

    if res.get("success"):
        print(f"[bold green]SUCCESS[/] Ad #{ad_number} posted successfully!")
        return True
    
    print(f'[bold red]ERROR[/] Failed to post Ad #{ad_number}: {res.get("message", "Unknown error")}')
    return False

def main():
    try:
        config = load_config()
        session = initialize_session(config.get("roli_verification"))
        player_id = int(config.get("player_id"))
        
        # Define two different trade ads
        trade_ads = [
            {
                "offer_items": [1048037, 1048037, 1048037, 564449640],  # Replace with your items
                "request_items": [],  # No specific request
                "request_tags": ["upgrade", "downgrade"],
                "name": "Ad 1 - Upgrades/Downgrades"
            },
            {
                "offer_items": [564449640, 9255011, 9255011, 9255011],  # Replace with different items
                "request_items": [],  # Requesting a specific item
                "request_tags": ["upgrade", "downgrade"],
                "name": "Ad 2 - Upgrades/Downgrades"
            },
            {
                 "offer_items": [162066176],  # Replace with different items
                "request_items": [],  # Requesting a specific item
                "request_tags": ["upgrade", "downgrade"],
                "name": "Ad 2 - Upgrades/Downgrades"
            }
        ]
        
        min_delay = 15  # minutes
        max_delay = 15  # minutes
        
        ad_counter = 0
        
        while True:
            current_ad = trade_ads[ad_counter % len(trade_ads)]  # Alternate between ads
            
            success = post_ad(
                session,
                player_id,
                current_ad["offer_items"],
                current_ad["request_items"],
                current_ad["request_tags"],
                current_ad["name"]
            )
            
            # Adjust delay based on success/failure
            delay_minutes = random.randint(
                min_delay if success else min_delay * 1,
                max_delay if success else max_delay * 1
            )
            
            print(f"\n[bold]Waiting {delay_minutes} minutes before next ad...[/]")
            time.sleep(delay_minutes * 60)
            
            ad_counter += 1  # Move to next ad
            
    except KeyboardInterrupt:
        print("\n[bold yellow]Script stopped by user[/]")
    except Exception as e:
        print(f"[bold red]Fatal error:[/] {e}")

if __name__ == "__main__":
    main()
