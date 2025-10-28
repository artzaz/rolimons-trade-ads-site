import json
import random
import time
import logging
from typing import Dict, List
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from rich.logging import RichHandler

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger("rolimons")

class ConfigError(Exception):
    """Custom exception for configuration errors"""
    pass

def load_config() -> Dict:
    """Load and validate configuration from config.json"""
    try:
        with open("config.json", encoding="utf-8") as f:
            config = json.load(f)
        
        # Validate required fields
        required_fields = ["roli_verification", "player_id", "trade_ads", "min_delay", "max_delay"]
        missing_fields = [field for field in required_fields if not config.get(field)]
        if missing_fields:
            raise ConfigError(f"Missing required config fields: {', '.join(missing_fields)}")
        
        # Validate player_id format
        try:
            config["player_id"] = int(config["player_id"])
        except ValueError:
            raise ConfigError("player_id must be a valid integer")
            
        return config
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Failed to load config: {e}")
        raise ConfigError(f"Failed to load config: {e}")

def initialize_session(verification_token: str) -> requests.Session:
    """Initialize a requests session with retry mechanism"""
    session = requests.Session()
    
    # Configure retry strategy
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json",
    })
    session.cookies.update({"_RoliVerification": verification_token})
    return session

def post_ad(
    session: requests.Session,
    player_id: int,
    offer_items: List[int],
    request_items: List[int],
    request_tags: List[str],
    ad_name: str
) -> bool:
    """Post a trade advertisement"""
    payload = {
        "player_id": player_id,
        "offer_item_ids": offer_items,
        "request_item_ids": request_items,
        "request_tags": request_tags
    }
    
    logger.info(f"\nPosting Trade Ad: {ad_name}")
    logger.info(f"➤ Offering: {offer_items}")
    logger.info(f"➤ Requesting: {request_items if request_items else 'Anything'} "
               f"({', '.join(request_tags) if request_tags else 'No tags'})")
    
    try:
        response = session.post(
            "https://api.rolimons.com/tradeads/v1/createad",
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        res = response.json()
    except requests.RequestException as e:
        logger.error(f"API request failed: {e}")
        return False
    except ValueError as e:
        logger.error(f"Invalid JSON response: {e}")
        return False

    if res.get("success"):
        logger.info(f"Ad '{ad_name}' posted successfully!")
        return True
    
    logger.error(f"Failed to post '{ad_name}': {res.get('message', 'Unknown error')}")
    return False

def main():
    """Main execution function"""
    try:
        config = load_config()
        session = initialize_session(config["roli_verification"])
        
        ad_counter = 0
        
        while True:
            current_ad = config["trade_ads"][ad_counter % len(config["trade_ads"])]
            
            success = post_ad(
                session=session,
                player_id=config["player_id"],
                offer_items=current_ad["offer_items"],
                request_items=current_ad["request_items"],
                request_tags=current_ad["request_tags"],
                ad_name=current_ad["name"]
            )
            
            delay_minutes = random.randint(
                config["min_delay"] if success else config["min_delay"] * 2,
                config["max_delay"] if success else config["max_delay"] * 2
            )
            
            logger.info(f"\nWaiting {delay_minutes} minutes before next ad...")
            time.sleep(delay_minutes * 60)
            
            ad_counter += 1
            
    except KeyboardInterrupt:
        logger.warning("\nScript stopped by user")
    except ConfigError as e:
        logger.error(f"Configuration error: {e}")
    except Exception as e:
        logger.exception(f"Fatal error: {e}")

if __name__ == "__main__":
    main()
