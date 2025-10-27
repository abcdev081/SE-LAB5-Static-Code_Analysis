"""
Simple inventory management module.

Provides functions to add/remove items, persist/load inventory to JSON,
and basic reporting. Uses safe patterns (no bare except, no eval,
no mutable default args) and basic input validation.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Union

# configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Module-level inventory store (keys are item names, values are numeric quantities).
stock_data: Dict[str, Union[int, float]] = {}


def add_item(item: str, qty: Union[int, float], logs: Optional[List[str]] = None) -> None:
    """Add quantity `qty` of `item` to the inventory.

    Args:
        item: Item name (string).
        qty: Quantity to add (positive int or float).
        logs: Optional list to append a timestamped entry to.
    Raises:
        TypeError: If types are incorrect.
        ValueError: If qty is negative or item is empty.
    """
    if not isinstance(item, str) or not item:
        raise TypeError("item must be a non-empty string")
    if not isinstance(qty, (int, float)):
        raise TypeError("qty must be an int or float")
    if qty < 0:
        raise ValueError("qty must be non-negative; use remove_item to decrement stock")

    # Update inventory
    current = stock_data.get(item, 0)
    stock_data[item] = current + qty

    # Log to provided list if present, else use logging
    timestamp = datetime.now()
    entry = f"{timestamp}: Added {qty} of {item}"
    if logs is None:
        logging.info(entry)
    else:
        logs.append(entry)


def remove_item(item: str, qty: Union[int, float]) -> None:
    """Remove quantity `qty` of `item` from the inventory.

    Args:
        item: Item name (string).
        qty: Quantity to remove (positive int or float).

    Raises:
        KeyError: If item not found.
        TypeError: If types are incorrect.
        ValueError: If qty is negative or greater than available stock.
    """
    if not isinstance(item, str) or not item:
        raise TypeError("item must be a non-empty string")
    if not isinstance(qty, (int, float)):
        raise TypeError("qty must be an int or float")
    if qty <= 0:
        raise ValueError("qty must be a positive number to remove")

    if item not in stock_data:
        raise KeyError(f"Item '{item}' not found in inventory")

    if stock_data[item] < qty:
        raise ValueError(f"Not enough '{item}' in stock to remove {qty}")

    stock_data[item] -= qty
    if stock_data[item] <= 0:
        del stock_data[item]


def get_qty(item: str) -> Union[int, float]:
    """Return quantity of `item` in inventory. Returns 0 if not present."""
    if not isinstance(item, str) or not item:
        raise TypeError("item must be a non-empty string")
    return stock_data.get(item, 0)


def load_data(file: str = "inventory.json") -> None:
    """Load inventory from a JSON file.

    If the file does not exist, the inventory remains unchanged (empty by default).
    Handles JSON decode errors gracefully.
    """
    try:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            logging.error("Loaded JSON is not a dict; ignoring file contents")
            return
        # update existing dict rather than reassign to avoid global statement
        stock_data.clear()
        # ensure numeric values
        for k, v in data.items():
            try:
                if not isinstance(k, str):
                    k = str(k)
                if not isinstance(v, (int, float)):
                    raise TypeError
                stock_data[k] = v
            except TypeError:
                logging.warning("Skipping invalid entry in JSON for key %r: %r", k, v)
    except FileNotFoundError:
        logging.info("Data file %s not found — starting with empty inventory", file)
    except json.JSONDecodeError as exc:
        logging.error("JSON decode error while loading %s: %s", file, exc)


def save_data(file: str = "inventory.json") -> None:
    """Save inventory to a JSON file (pretty-printed)."""
    try:
        with open(file, "w", encoding="utf-8") as f:
            json.dump(stock_data, f, ensure_ascii=False, indent=2)
        logging.info("Inventory saved to %s", file)
    except OSError as exc:
        logging.error("Error writing to %s: %s", file, exc)


def print_data() -> None:
    """Print a simple items report via logging."""
    logging.info("Items Report")
    if not stock_data:
        logging.info("  (no items in inventory)")
    for name, qty in stock_data.items():
        logging.info("  %s -> %s", name, qty)


def check_low_items(threshold: Union[int, float] = 5) -> List[str]:
    """Return list of items with quantity strictly less than threshold."""
    if not isinstance(threshold, (int, float)):
        raise TypeError("threshold must be numeric")
    return [name for name, qty in stock_data.items() if qty < threshold]


def main() -> None:
    """Demonstration of inventory functions with safe calls."""
    # Example usage and demonstration. Adjust/remove in production.
    try:
        add_item("apple", 10)
        add_item("banana", 2)
        # Example of validating bad input (this will raise; kept commented to show correct usage)
        # add_item(123, "ten")  # invalid types — will raise TypeError if used
        remove_item("apple", 3)
    except (TypeError, ValueError, KeyError) as exc:
        logging.error("Operation failed: %s", exc)

    logging.info("Apple stock: %s", get_qty("apple"))
    logging.info("Low items: %s", check_low_items())

    save_data()
    load_data()
    print_data()


if __name__ == "__main__":
    main()
