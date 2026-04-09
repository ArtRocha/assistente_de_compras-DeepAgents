import json
import os
import re
from typing import Iterable, List, Optional
from urllib.parse import parse_qs, unquote, urljoin, urlparse

import httpx
from bs4 import BeautifulSoup, Tag

from ..schemas.product import Product


class SearchAPI:
    """Searches product offers on Google Shopping via SerpAPI (primary) with
    direct-scrape fallback. SerpAPI bypasses Google bot-detection that causes
    the JS-redirect page returned to server/WSL IPs.

    Set SERPAPI_KEY env var to enable real searches.
    Without the key the scraper falls back to mock data so the pipeline doesn't break.
    """

    _GOOGLE_BASE = "https://www.google.com"
    _SEARCH_URL = f"{_GOOGLE_BASE}/search"
    _SERPAPI_URL = "https://serpapi.com/search.json"
    _PRICE_PATTERN = re.compile(r"(?:R\$|\$|BRL)\s*([\d\.,]+)", flags=re.IGNORECASE)
    _NUMERIC_PRICE_PATTERN = re.compile(r"\b\d{1,3}(?:\.\d{3})*(?:,\d{2})\b|\b\d+(?:\.\d{2})\b")

    async def search(self, query: str) -> List[Product]:
        normalized_query = query.strip()
        if not normalized_query:
            return []

        serpapi_key = os.getenv("SERPAPI_KEY", "").strip()

        if serpapi_key:
            print(f"[SearchAPI] Usando SerpAPI para: '{normalized_query}'")
            results = await self._search_via_serpapi(normalized_query, serpapi_key)
            if results:
                print(f"[SearchAPI] SerpAPI retornou {len(results)} resultados.")
                return results
            print("[SearchAPI] SerpAPI retornou vazio, tentando scraping direto...")

        # Fallback: scraping direto (funciona em IPs residenciais, falha em servidores)
        print(f"[SearchAPI] Tentando scraping direto para: '{normalized_query}'")
        html = await self._fetch_google_shopping_html(normalized_query)
        if not html:
            print(f"[SearchAPI] AVISO: scraping direto não retornou HTML válido para '{normalized_query}'.")
            print("[SearchAPI] CAUSA PROVÁVEL: Google está retornando redirect JS para este IP (comum em servidores/WSL).")
            print("[SearchAPI] SOLUÇÃO: Defina SERPAPI_KEY no ambiente para usar a API oficial.")
            return []

        parsed = self._parse_google_shopping_html(html, normalized_query)
        if not parsed:
            print(f"[SearchAPI] AVISO: HTML recebido mas nenhum card de produto encontrado para '{normalized_query}'.")
            print("[SearchAPI] CAUSA PROVÁVEL: Google mudou o layout (udm=28) ou retornou página de redirect JS.")
        else:
            print(f"[SearchAPI] Scraping direto retornou {len(parsed)} resultados.")
        return parsed

    async def _search_via_serpapi(self, query: str, api_key: str) -> List[Product]:
        """Busca via SerpAPI Google Shopping — retorna dados estruturados em JSON."""
        params = {
            "engine": "google_shopping",
            "q": query,
            "hl": "pt",
            "gl": "br",
            "api_key": api_key,
            "num": "20",
        }
        try:
            async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
                response = await client.get(self._SERPAPI_URL, params=params)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as e:
            print(f"[SearchAPI] SerpAPI HTTP {e.response.status_code} para '{query}': {e}")
            return []
        except httpx.TimeoutException:
            print(f"[SearchAPI] SerpAPI timeout para '{query}'")
            return []
        except Exception as e:
            print(f"[SearchAPI] ERRO ao chamar SerpAPI para '{query}': {e}")
            return []

        shopping_results = data.get("shopping_results", [])
        if not shopping_results:
            # Verificar se há erro de API
            error = data.get("error")
            if error:
                print(f"[SearchAPI] SerpAPI retornou erro: {error}")
            else:
                print(f"[SearchAPI] SerpAPI: nenhum shopping_result na resposta para '{query}'")
            return []

        products: List[Product] = []
        seen_keys: set = set()

        for item in shopping_results:
            title = str(item.get("title", "")).strip()
            raw_price = item.get("extracted_price") or item.get("price", "")
            store = str(item.get("source", "")).strip()

            # Priorizar URL direta da loja; 'link' é URL interna do Google Shopping
            url = (
                str(item.get("product_link", "")).strip()
                or str(item.get("link", "")).strip()
            )

            # Parsear preço
            if isinstance(raw_price, (int, float)):
                price = float(raw_price)
            else:
                price = self._parse_price(str(raw_price))

            if not title or price is None or not url:
                continue

            if not store:
                store = self._extract_store_from_url(url)

            dedupe_key = f"{title.lower()}::{store.lower()}::{price:.2f}"
            if dedupe_key in seen_keys:
                continue
            seen_keys.add(dedupe_key)

            products.append(
                Product(
                    title=title,
                    price=price,
                    store=store or "Loja não informada",
                    url=url,
                    source="google_shopping_serpapi",
                )
            )

            if len(products) >= 20:
                break

        return products

    async def _fetch_google_shopping_html(self, query: str) -> str:
        params = {
            "q": query,
            "tbm": "shop",
            "hl": "pt-BR",
            "gl": "br",
            "num": "20",
        }

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            # Sem Accept-Encoding para forçar texto plano (evitar binário comprimido)
        }

        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(self._SEARCH_URL, params=params, headers=headers)
                response.raise_for_status()
                html = response.text

                # Detectar redirect JS (sinal de bloqueio por bot-detection)
                low = html.lower()
                if (
                    "redirecionamento não iniciar" in low
                    or "unusual traffic" in low
                    or "captcha" in low
                    or "<html" not in low
                    or len(html) < 5000
                ):
                    print(
                        f"[SearchAPI] Google retornou página de bloqueio/redirect para '{query}'. "
                        f"HTML size={len(html)}, URL final={response.url}"
                    )
                    return ""

                return html
        except httpx.HTTPStatusError as e:
            print(f"[SearchAPI] ERRO HTTP {e.response.status_code} ao buscar '{query}': {e}")
            return ""
        except httpx.TimeoutException:
            print(f"[SearchAPI] TIMEOUT ao buscar '{query}' no Google Shopping")
            return ""
        except Exception as e:
            print(f"[SearchAPI] ERRO ao buscar dados no Google Shopping para '{query}': {e}")
            return ""

    def _parse_google_shopping_html(self, html: str, query: str) -> List[Product]:
        soup = BeautifulSoup(html, "html.parser")

        products_from_json = self._parse_products_from_json_ld(soup)
        if products_from_json:
            return self._dedupe_products(products_from_json)[:20]

        cards = self._find_product_cards(soup)

        products: List[Product] = []
        seen_keys = set()

        for card in cards:
            title = self._extract_title(card, soup)
            price = self._extract_price(card)
            store = self._extract_store(card)
            raw_link = self._extract_link(card)
            url = self._normalize_product_url(raw_link)

            card_text_context = self._extract_text_context(card)
            if price is None:
                price = self._parse_price(card_text_context)
            if not store:
                store = self._extract_store_from_text(card_text_context)

            aria_label = str(card.get("aria-label", "")).strip()
            if price is None and aria_label:
                price = self._parse_price(aria_label)
            if not store and aria_label:
                store = self._extract_store_from_text(aria_label)

            if not title or price is None:
                continue

            if not url or self._is_search_results_link(url):
                continue

            if not store:
                store = self._extract_store_from_url(url)

            dedupe_key = f"{title.lower()}::{store.lower()}::{price:.2f}"
            if dedupe_key in seen_keys:
                continue
            seen_keys.add(dedupe_key)

            products.append(
                Product(
                    title=title,
                    price=price,
                    store=store or "Loja nao informada",
                    url=url,
                    source="google_shopping_live",
                )
            )

            if len(products) >= 20:
                break

        return self._dedupe_products(products)

    def _parse_products_from_json_ld(self, soup: BeautifulSoup) -> List[Product]:
        products: List[Product] = []
        scripts = soup.select("script[type='application/ld+json']")
        for script in scripts:
            raw_json = (script.string or script.get_text() or "").strip()
            if not raw_json:
                continue

            try:
                parsed = json.loads(raw_json)
            except json.JSONDecodeError:
                continue

            nodes: Iterable[object] = parsed if isinstance(parsed, list) else [parsed]
            for node in nodes:
                if not isinstance(node, dict):
                    continue

                items = node.get("itemListElement")
                if not isinstance(items, list):
                    continue

                for item in items:
                    if not isinstance(item, dict):
                        continue

                    product_node = item.get("item", item)
                    if not isinstance(product_node, dict):
                        continue

                    title = str(product_node.get("name", "")).strip()
                    offers = product_node.get("offers", {})
                    if isinstance(offers, list):
                        offers = offers[0] if offers else {}
                    if not isinstance(offers, dict):
                        offers = {}

                    price = self._parse_price(str(offers.get("price", "")))
                    if price is None:
                        price = self._parse_price(str(product_node.get("price", "")))
                    url = str(offers.get("url") or product_node.get("url") or "").strip()

                    seller = offers.get("seller", {})
                    if isinstance(seller, dict):
                        store = str(seller.get("name", "")).strip()
                    else:
                        store = str(seller).strip()

                    if not title or price is None:
                        continue

                    normalized_url = self._normalize_product_url(url)
                    if not normalized_url or self._is_search_results_link(normalized_url):
                        continue

                    products.append(
                        Product(
                            title=title,
                            price=price,
                            store=store or self._extract_store_from_url(normalized_url) or "Loja nao informada",
                            url=normalized_url,
                            source="google_shopping_live",
                        )
                    )

        return products

    def _find_product_cards(self, soup: BeautifulSoup) -> List[Tag]:
        known_selectors = [
            # Layout clássico (pré-2024)
            "div.sh-dgr__grid-result",
            "div.sh-dlr__list-result",
            "div.sh-dgr__content",
            "div.sh-dlr__content",
            "div[data-docid]",
            "div[data-rw]",
            "a.plantl.clickable-card",
            "a.pla-unit-single-clickable-target",
            "a[data-offer-id][href]",
            # Layout novo udm=28 (2024+)
            "div.KZmu8e",
            "div.i0X6df",
            "li[jsdata]",
            "div[data-sh-gr]",
            "div.mnr-c",
        ]

        cards: List[Tag] = []
        seen_ids = set()

        for selector in known_selectors:
            for card in soup.select(selector):
                marker = id(card)
                if marker in seen_ids:
                    continue
                seen_ids.add(marker)
                cards.append(card)

        if cards:
            return cards

        for div in soup.find_all("div"):
            if not isinstance(div, Tag):
                continue

            text = div.get_text(" ", strip=True)
            if not text or len(text) > 800:
                continue
            if not self._PRICE_PATTERN.search(text) and not self._NUMERIC_PRICE_PATTERN.search(text):
                continue
            if not div.find("a", href=True):
                continue

            cards.append(div)
            if len(cards) >= 80:
                break

        return cards

    def _extract_title(self, card: Tag, soup: BeautifulSoup) -> str:
        candidates = [
            card.select_one("h3.tAxDx"),
            card.select_one("h4.A2sOrd"),
            card.select_one("div.Xjkr3b"),
            card.select_one("a.shntl"),
            card.select_one("h3"),
            card.select_one("h4"),
            card.select_one("a[title]"),
        ]
        for candidate in candidates:
            if candidate and candidate.get_text(strip=True):
                return candidate.get_text(strip=True)

        link = card.find("a", href=True)
        if link and link.get("title"):
            return str(link.get("title")).strip()

        title_id = str(card.get("data-title-id", "")).strip()
        if title_id:
            node = soup.find(id=title_id)
            if isinstance(node, Tag):
                title_text = node.get_text(" ", strip=True)
                if title_text:
                    return title_text

        aria_label = str(card.get("aria-label", "")).strip()
        if aria_label:
            cleaned = re.sub(r"\bpor\b.*", "", aria_label, flags=re.IGNORECASE).strip()
            if cleaned:
                return cleaned

        return ""

    def _extract_price(self, card: Tag) -> Optional[float]:
        candidates = [
            card.select_one("span.a8Pemb"),
            card.select_one("span.T14wmb"),
            card.select_one("span.e10twf"),
            card.select_one("span[aria-label*='R$']"),
            card.select_one("div[aria-label*='R$']"),
        ]

        for candidate in candidates:
            if candidate:
                parsed = self._parse_price(candidate.get_text(" ", strip=True))
                if parsed is not None:
                    return parsed

        text = card.get_text(" ", strip=True)
        return self._parse_price(text)

    def _extract_store(self, card: Tag) -> str:
        candidates = [
            card.select_one("div.aULzUe"),
            card.select_one("span.aULzUe"),
            card.select_one("div.IuHnof"),
            card.select_one("span[aria-label*='Loja']"),
            card.select_one("div[aria-label*='Loja']"),
        ]

        for candidate in candidates:
            if candidate and candidate.get_text(strip=True):
                return candidate.get_text(strip=True)

        text = card.get_text(" ", strip=True)
        match = re.search(r"(?:por|de)\s+([A-Za-z0-9\.\-\s]{2,50})", text, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()

        aria_label = str(card.get("aria-label", "")).strip()
        if aria_label:
            return self._extract_store_from_text(aria_label)

        return ""

    def _extract_link(self, card: Tag) -> str:
        prioritized = card.select(
            "a.shntl, a[href*='/url?'], a[href*='/shopping/product/'], a[href]"
        )

        for link in prioritized:
            href = str(link.get("href", "")).strip()
            if href:
                return href

        return ""

    def _normalize_product_url(self, raw_url: str) -> str:
        if not raw_url:
            return ""

        absolute = urljoin(self._GOOGLE_BASE, raw_url)
        parsed = urlparse(absolute)

        if parsed.netloc.endswith("google.com"):
            query_data = parse_qs(parsed.query)
            target = (
                query_data.get("q", [""])[0]
                or query_data.get("url", [""])[0]
                or query_data.get("adurl", [""])[0]
                or query_data.get("u", [""])[0]
            )
            if target:
                return unquote(target)

        return absolute

    def _parse_price(self, text: str) -> Optional[float]:
        cleaned = text.replace("\xa0", " ").strip()
        if not cleaned:
            return None

        match = self._PRICE_PATTERN.search(cleaned)
        candidate = match.group(1) if match else ""

        if not candidate:
            numeric_match = self._NUMERIC_PRICE_PATTERN.search(cleaned)
            if numeric_match:
                candidate = numeric_match.group(0)
            else:
                return None

        normalized = candidate.replace(" ", "")
        if "," in normalized and "." in normalized:
            normalized = normalized.replace(".", "").replace(",", ".")
        elif "," in normalized:
            normalized = normalized.replace(".", "").replace(",", ".")
        else:
            parts = normalized.split(".")
            if len(parts) > 2:
                normalized = "".join(parts)

        try:
            value = float(normalized)
        except ValueError:
            return None

        return value if value > 0 else None

    def _extract_store_from_url(self, url: str) -> str:
        host = urlparse(url).netloc.lower()
        if host.startswith("www."):
            host = host[4:]
        if not host:
            return ""
        return host.split(".")[0].replace("-", " ").title()

    def _extract_store_from_text(self, text: str) -> str:
        match = re.search(r"\b(?:de|por)\s+([A-Za-z0-9\.\-\s]{2,60})", text, flags=re.IGNORECASE)
        if not match:
            return ""
        return match.group(1).strip()

    def _extract_text_context(self, card: Tag) -> str:
        chunks: List[str] = []

        own_text = card.get_text(" ", strip=True)
        if own_text:
            chunks.append(own_text)

        parent = card.parent if isinstance(card.parent, Tag) else None
        if parent:
            parent_text = parent.get_text(" ", strip=True)
            if parent_text:
                chunks.append(parent_text)

            grand_parent = parent.parent if isinstance(parent.parent, Tag) else None
            if grand_parent:
                gp_text = grand_parent.get_text(" ", strip=True)
                if gp_text:
                    chunks.append(gp_text)

        return " ".join(chunks)

    def _is_search_results_link(self, url: str) -> bool:
        parsed = urlparse(url)
        if not parsed.netloc.endswith("google.com"):
            return False

        if parsed.path in {"/search", "/"}:
            return True

        query_data = parse_qs(parsed.query)
        return "udm" in query_data or "tbm" in query_data

    def _dedupe_products(self, products: List[Product]) -> List[Product]:
        deduped: List[Product] = []
        seen_urls = set()
        seen_identity = set()

        for product in products:
            url_key = product.url.strip().lower()
            identity_key = (
                product.title.strip().lower(),
                product.store.strip().lower(),
                round(product.price, 2),
            )

            if url_key and url_key in seen_urls:
                continue
            if identity_key in seen_identity:
                continue

            if url_key:
                seen_urls.add(url_key)
            seen_identity.add(identity_key)
            deduped.append(product)

        return deduped
