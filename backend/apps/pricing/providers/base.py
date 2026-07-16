"""
Normalized grocery provider interface + matching helpers.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Optional


@dataclass
class ProviderProduct:
    """Normalized product payload returned by any grocery provider.

    This is the single normalized schema shared by every provider
    (Blinkit, Zepto, Instamart, BigBasket, Fake). ``price`` is the selling
    price; ``selling_price`` is exposed as an alias for readability.
    """

    external_id: str
    name: str
    price: Decimal
    in_stock: bool = True
    image_url: Optional[str] = None
    product_url: Optional[str] = None
    brand: Optional[str] = None
    unit: Optional[str] = None
    mrp: Optional[Decimal] = None
    delivery_eta: Optional[str] = None
    source: Optional[str] = None
    barcode: Optional[str] = None
    store: Optional[str] = None
    raw: dict = field(default_factory=dict)

    @property
    def selling_price(self) -> Decimal:
        return self.price

    def to_result(self) -> dict:
        """Return the canonical normalized dict every provider must produce."""
        return {
            "name": self.name,
            "brand": self.brand,
            "unit": self.unit,
            "image_url": self.image_url,
            "product_url": self.product_url,
            "mrp": self.mrp,
            "selling_price": self.price,
            "in_stock": self.in_stock,
            "delivery_eta": self.delivery_eta,
            "source": self.source or self.store,
            "raw": self.raw,
        }


_TOKEN_RE = re.compile(r"[a-z0-9]+")
_UNIT_RE = re.compile(
    r"(\d+(?:\.\d+)?)\s*(kg|g|gm|grams?|ml|l|ltr|litre|liter|pack|pcs|piece|pieces)\b",
    re.I,
)


def normalize_name(name: str) -> str:
    return " ".join(_TOKEN_RE.findall((name or "").lower()))


def extract_unit(text: str) -> Optional[str]:
    match = _UNIT_RE.search(text or "")
    if not match:
        return None
    value, unit = match.group(1), match.group(2).lower()
    unit = {"gm": "g", "gram": "g", "grams": "g", "ltr": "l", "litre": "l", "liter": "l"}.get(
        unit, unit
    )
    return f"{value}{unit}"


def styled_text(value: Any) -> Optional[str]:
    """Blinkit/Zepto often wrap display strings as ``{\"text\": \"...\"}`` objects."""
    if value is None:
        return None
    if isinstance(value, dict):
        inner = value.get("text")
        if inner is None:
            inner = value.get("value") or value.get("price") or value.get("title")
        return styled_text(inner)
    text = str(value).strip()
    return text or None


def parse_money(value: Any, *, paise: bool = False) -> Optional[Decimal]:
    """Parse a price that may be styled text, INR with ₹, or paise integers."""
    if value is None:
        return None
    if isinstance(value, dict):
        return parse_money(
            value.get("value") or value.get("price") or value.get("text") or value.get("mrp"),
            paise=paise,
        )
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        amount = Decimal(str(value))
        if paise:
            amount = amount / Decimal(100)
        return amount
    text = str(value).replace("₹", "").replace(",", "").strip()
    if not text:
        return None
    try:
        amount = Decimal(text)
    except Exception:
        return None
    if paise:
        amount = amount / Decimal(100)
    return amount


def build_product(
    *,
    source: str,
    external_id: Any,
    name: Any,
    price: Any,
    mrp: Any = None,
    in_stock: Any = True,
    image_url: Any = None,
    product_url: Optional[str] = None,
    brand: Any = None,
    unit: Any = None,
    delivery_eta: Optional[str] = None,
    barcode: Optional[str] = None,
    raw: Optional[dict] = None,
    paise: bool = False,
) -> Optional[ProviderProduct]:
    """Single normalization entry point shared by every provider.

    Centralizes money/text parsing so parsing logic is not duplicated across
    provider modules. Returns ``None`` when the minimum viable fields
    (name + price + id) cannot be resolved.
    """
    name_s = styled_text(name)
    price_d = price if isinstance(price, Decimal) else parse_money(price, paise=paise)
    if not name_s or price_d is None or external_id is None:
        return None

    if isinstance(mrp, Decimal):
        mrp_d: Optional[Decimal] = mrp
    else:
        mrp_d = parse_money(mrp, paise=paise) if mrp is not None else None

    image = None
    if isinstance(image_url, (list, tuple)):
        image = next((i for i in image_url if i), None)
    else:
        image = image_url

    if isinstance(in_stock, str):
        in_stock_b = in_stock.strip().lower() not in ("false", "0", "no", "out_of_stock")
    else:
        in_stock_b = bool(in_stock)

    return ProviderProduct(
        external_id=str(external_id).strip("'\""),
        name=name_s,
        price=price_d,
        mrp=mrp_d,
        in_stock=in_stock_b,
        image_url=str(image) if image else None,
        product_url=product_url,
        brand=styled_text(brand),
        unit=styled_text(unit) or extract_unit(name_s),
        delivery_eta=str(delivery_eta) if delivery_eta else None,
        source=source,
        store=source,
        barcode=barcode,
        raw=raw or {},
    )


def fuzzy_score(
    query: str,
    candidate: str,
    *,
    brand: Optional[str] = None,
    candidate_brand: Optional[str] = None,
    catalog_unit: Optional[str] = None,
    candidate_unit: Optional[str] = None,
) -> float:
    """
    Token Jaccard + brand/unit bonuses. Returns 0..2+.
    """
    q = normalize_name(query)
    c = normalize_name(candidate)
    if not q or not c:
        return 0.0
    if q == c:
        overlap = 1.5
    else:
        qt, ct = set(q.split()), set(c.split())
        if not qt or not ct:
            return 0.0
        overlap = len(qt & ct) / len(qt | ct)

    qu = catalog_unit or extract_unit(query)
    cu = candidate_unit or extract_unit(candidate)
    if qu and cu and qu == cu:
        overlap += 0.5
    elif qu and cu:
        # Handle "500g" catalog vs "1 pack (500 g)" provider units
        qu_num = re.sub(r"[^0-9.]", "", qu)
        cu_num = re.sub(r"[^0-9.]", "", cu)
        qu_kind = re.sub(r"[0-9.]", "", qu)
        cu_kind = re.sub(r"[0-9.]", "", cu)
        if qu_num and qu_num == cu_num and qu_kind == cu_kind:
            overlap += 0.45

    if brand and candidate_brand:
        bn = normalize_name(brand)
        cbn = normalize_name(str(candidate_brand))
        if bn and cbn:
            if bn == cbn:
                overlap += 0.35
            elif bn in cbn or cbn in bn:
                overlap += 0.15

    # brand-ish first token match
    if q.split()[0] == c.split()[0]:
        overlap += 0.1
    return overlap


def catalog_search_queries(product) -> list[str]:
    """Build provider search queries from a catalog Product."""
    name = (getattr(product, "name", None) or "").strip()
    brand_name = ""
    if getattr(product, "brand", None) is not None:
        brand_name = getattr(product.brand, "name", None) or str(product.brand)

    queries: list[str] = []
    if name:
        queries.append(name)

    unit = extract_unit(name)
    core = name
    if unit:
        core = re.sub(re.escape(unit), "", name, flags=re.I)
        core = re.sub(r"\b\d+\s*(kg|g|gm|ml|l|ltr|litre|liter|pack|pcs)\b", "", core, flags=re.I)
        core = " ".join(core.split()).strip(" -")

    if brand_name and core:
        queries.append(f"{brand_name} {core}".strip())
    if brand_name and name.lower().startswith(brand_name.lower()):
        stripped = name[len(brand_name) :].strip()
        if stripped:
            queries.append(f"{brand_name} {stripped}".strip())

    # Preserve order, drop duplicates
    seen: set[str] = set()
    unique: list[str] = []
    for q in queries:
        key = q.lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(q)
    return unique


class BaseProvider(ABC):
    """Common interface implemented by Blinkit, Zepto, Instamart, aggregators."""

    name: str = "base"
    store_slug: str = "base"

    @abstractmethod
    def search(self, query: str, *, limit: int = 10) -> list[ProviderProduct]:
        """Search the provider catalog for products matching `query`."""

    def search_products(self, query: str, *, limit: int = 10) -> list[ProviderProduct]:
        return self.search(query, limit=limit)

    def _finalize(self, products: list[ProviderProduct]) -> list[ProviderProduct]:
        """Ensure every result carries a consistent source/store label."""
        for item in products:
            if not item.source:
                item.source = self.name
            if not item.store:
                item.store = self.name
        return products

    @abstractmethod
    def get_product(self, external_id: str) -> Optional[ProviderProduct]:
        """Fetch a single product by provider-specific id."""

    def get_current_price(self, external_id: str) -> Optional[Decimal]:
        product = self.get_product(external_id)
        return product.price if product else None

    # Alias kept for older call sites
    def get_price(self, external_id: str) -> Optional[Decimal]:
        return self.get_current_price(external_id)

    def get_availability(self, external_id: str) -> Optional[bool]:
        product = self.get_product(external_id)
        return product.in_stock if product else None

    def get_store(self) -> str:
        return self.name

    def fetch_price_for_catalog_product(self, product) -> Optional[dict]:
        """
        Resolve a PricePulse catalog Product against this provider.

        Returns a dict compatible with PriceService.update_price.
        """
        brand_name = None
        if getattr(product, "brand", None) is not None:
            brand_name = getattr(product.brand, "name", None) or str(product.brand)

        catalog_unit = extract_unit(product.name)
        results: list[ProviderProduct] = []
        for query in catalog_search_queries(product):
            results = self.search(query, limit=12)
            if results:
                break

        if not results:
            return None

        barcode = getattr(product, "barcode", None)
        match = self._best_match(
            product.name,
            results,
            barcode=barcode,
            brand=brand_name,
            catalog_unit=catalog_unit,
        )
        if not match:
            return None

        return {
            "price": match.price,
            "mrp": match.mrp,
            "in_stock": match.in_stock,
            "product_url": match.product_url,
            "image_url": match.image_url,
            "delivery_eta": match.delivery_eta,
            "external_id": match.external_id,
            "normalized_name": match.name,
            "unit": match.unit,
            "brand": match.brand,
            "source": match.source or self.name,
        }

    @staticmethod
    def _best_match(
        query: str,
        results: list[ProviderProduct],
        *,
        barcode: Optional[str] = None,
        brand: Optional[str] = None,
        catalog_unit: Optional[str] = None,
    ) -> Optional[ProviderProduct]:
        if barcode:
            for item in results:
                if item.barcode and item.barcode == barcode:
                    return item

        def score(item: ProviderProduct) -> float:
            item_unit = extract_unit(item.unit or "") or extract_unit(item.name)
            return fuzzy_score(
                query,
                item.name,
                brand=brand,
                candidate_brand=item.brand,
                catalog_unit=catalog_unit,
                candidate_unit=item_unit,
            )

        ranked = sorted(results, key=score, reverse=True)
        if not ranked:
            return None
        if score(ranked[0]) < 0.15:
            return None
        return ranked[0]
