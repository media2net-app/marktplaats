"""
Utility functions voor Marktplaats automatisering
"""
import os
from typing import List, Optional
from dataclasses import dataclass


ALLOWED_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".heic"}

# Environment variables
VERBOSE = os.getenv("MP_VERBOSE", "true").lower() in ("1", "true", "yes", "on")
FAST_MODE = os.getenv("MP_FAST", "true").lower() in ("1", "true", "yes", "on")

# Wait time constants - shorter in fast mode
WAIT_SHORT = 100 if FAST_MODE else 300
WAIT_MEDIUM = 300 if FAST_MODE else 600
WAIT_LONG = 500 if FAST_MODE else 1000
WAIT_NAVIGATION = 800 if FAST_MODE else 1500


def log_step(message: str) -> None:
    """Log een stap in het proces"""
    if VERBOSE:
        print(f"[STEP] {message}")


def log_error(message: str) -> None:
    """Log een fout"""
    print(f"[ERROR] {message}")


def log_success(message: str) -> None:
    """Log een succesvolle actie"""
    print(f"[OK] {message}")


def log_warning(message: str) -> None:
    """Log een waarschuwing"""
    print(f"[WARNING] {message}")


@dataclass
class Product:
    """Product data class voor Marktplaats advertenties"""
    title: str
    description: str
    price: str
    category_path: Optional[str] = None
    location: Optional[str] = None
    photos: List[str] = None
    article_number: Optional[str] = None
    condition: Optional[str] = None
    delivery_methods: List[str] = None
    material: Optional[str] = None
    thickness: Optional[str] = None
    total_surface: Optional[str] = None
    delivery_option: Optional[str] = None
    category_fields: Optional[dict] = None
    
    def __post_init__(self):
        if self.photos is None:
            self.photos = []
        if self.delivery_methods is None:
            self.delivery_methods = []


def find_photos_for_article(media_root: str, article_number: str) -> List[str]:
    """Zoek foto's voor een artikelnummer in de media root directory"""
    if not article_number:
        return []
    
    # Try exact match first
    folder = os.path.join(media_root, str(article_number))
    if os.path.isdir(folder):
        files = _get_photos_from_folder(folder)
        if files:
            return files
    
    # Try variations (replace special characters, spaces, etc.)
    variations = [
        article_number.replace('/', '-').replace(' ', '-'),
        article_number.replace('/', '_').replace(' ', '_'),
        article_number.replace(' ', '-'),
        article_number.replace(' ', '_'),
        article_number.replace('/', '-'),
    ]
    
    for variant in variations:
        if variant == article_number:  # Skip if same as original
            continue
        folder = os.path.join(media_root, variant)
        if os.path.isdir(folder):
            files = _get_photos_from_folder(folder)
            if files:
                return files
    
    # Try to find folder that contains article number (partial match)
    if os.path.isdir(media_root):
        try:
            for item in os.listdir(media_root):
                item_path = os.path.join(media_root, item)
                if os.path.isdir(item_path):
                    # Check if article number is in folder name or vice versa
                    article_clean = article_number.lower().replace(' ', '').replace('-', '').replace('_', '')
                    item_clean = item.lower().replace(' ', '').replace('-', '').replace('_', '')
                    if article_clean in item_clean or item_clean in article_clean:
                        files = _get_photos_from_folder(item_path)
                        if files:
                            return files
        except:
            pass
    
    return []


def _get_photos_from_folder(folder: str) -> List[str]:
    """Haal foto's op uit een folder"""
    files: List[str] = []
    try:
        for name in sorted(os.listdir(folder)):
            path = os.path.join(folder, name)
            if not os.path.isfile(path):
                continue
            ext = os.path.splitext(name)[1].lower()
            if ext in ALLOWED_IMAGE_EXTS:
                files.append(os.path.abspath(path))
    except:
        pass
    return files


def normalize_price(price: str) -> str:
    """Normaliseer prijs naar Nederlands formaat (komma als decimaal)"""
    price_str = str(price).strip()
    
    # Als er een punt is en geen komma, en het is een nummer, vervang punt met komma
    if '.' in price_str and ',' not in price_str:
        try:
            float(price_str)  # Check of het een geldig nummer is
            price_str = price_str.replace('.', ',')
        except ValueError:
            pass  # Niet een nummer, laat zoals het is
    
    # Verwijder spaties
    price_str = price_str.replace(' ', '')
    
    return price_str
