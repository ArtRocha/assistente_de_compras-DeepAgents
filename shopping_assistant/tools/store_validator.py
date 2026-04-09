from __future__ import annotations

from typing import Any, Dict, List
from urllib.parse import urlparse


class StoreValidationEngine:
    """Evaluates store confidence with objective reputation and security metrics."""

    _STORE_METRICS: Dict[str, Dict[str, Any]] = {
        "amazon": {
            "display_name": "Amazon",
            "reclame_aqui_rating": 8.8,
            "trustpilot_rating": 1.9,
            "response_rate": 0.98,
            "resolution_rate": 0.93,
            "years_online": 29,
            "official_domains": ["amazon.com.br", "amazon.com"],
        },
        "mercadolivre": {
            "display_name": "Mercado Livre",
            "reclame_aqui_rating": 7.4,
            "trustpilot_rating": 1.5,
            "response_rate": 0.87,
            "resolution_rate": 0.79,
            "years_online": 25,
            "official_domains": ["mercadolivre.com.br", "mercadolivre.com"],
        },
        "magalu": {
            "display_name": "Magalu",
            "reclame_aqui_rating": 9.1,
            "trustpilot_rating": 1.5,
            "response_rate": 0.99,
            "resolution_rate": 0.95,
            "years_online": 67,
            "official_domains": ["magazineluiza.com.br", "magalu.com"],
        },
        "fastshop": {
            "display_name": "Fast Shop",
            "reclame_aqui_rating": 8.7,
            "trustpilot_rating": 2.2,
            "response_rate": 0.96,
            "resolution_rate": 0.91,
            "years_online": 38,
            "official_domains": ["fastshop.com.br"],
        },
        "kabum": {
            "display_name": "Kabum",
            "reclame_aqui_rating": 8.4,
            "trustpilot_rating": 2.4,
            "response_rate": 0.95,
            "resolution_rate": 0.88,
            "years_online": 22,
            "official_domains": ["kabum.com.br"],
        },
        "casasbahia": {
            "display_name": "Casas Bahia",
            "reclame_aqui_rating": 8.0,
            "trustpilot_rating": 1.4,
            "response_rate": 0.91,
            "resolution_rate": 0.82,
            "years_online": 72,
            "official_domains": ["casasbahia.com.br"],
        },
        "ponto": {
            "display_name": "Ponto",
            "reclame_aqui_rating": 6.4,
            "trustpilot_rating": 1.7,
            "response_rate": 0.74,
            "resolution_rate": 0.61,
            "years_online": 76,
            "official_domains": ["ponto.com.br"],
        },
        "olx": {
            "display_name": "OLX",
            "reclame_aqui_rating": 5.9,
            "trustpilot_rating": 1.3,
            "response_rate": 0.70,
            "resolution_rate": 0.58,
            "years_online": 19,
            "official_domains": ["olx.com.br"],
        },
    }

    _SUSPICIOUS_TLDS = {"click", "xyz", "top", "gq", "support", "work"}

    async def validate_store(self, store_name: str, product_url: str) -> Dict[str, Any]:
        normalized_store = self._normalize_store_name(store_name)
        baseline = self._STORE_METRICS.get(
            normalized_store,
            {
                "display_name": store_name,
                "reclame_aqui_rating": 5.5,
                "trustpilot_rating": 2.0,
                "response_rate": 0.60,
                "resolution_rate": 0.55,
                "years_online": 3,
                "official_domains": [],
            },
        )

        domain = self._extract_domain(product_url)
        domain_match = self._compute_domain_match_score(domain, baseline["official_domains"], normalized_store)
        https_score = 1.0 if product_url.lower().startswith("https://") else 0.0
        domain_reputation = self._compute_domain_reputation_score(domain)
        security_score = round((https_score * 0.35) + (domain_match * 0.45) + (domain_reputation * 0.20), 4)

        ra_score = float(baseline["reclame_aqui_rating"]) / 10.0
        trustpilot_score = float(baseline["trustpilot_rating"]) / 5.0
        response_rate = float(baseline["response_rate"])
        resolution_rate = float(baseline["resolution_rate"])
        years_online_score = min(float(baseline["years_online"]) / 20.0, 1.0)

        reputation_score = round(
            (ra_score * 0.45)
            + (trustpilot_score * 0.15)
            + (response_rate * 0.20)
            + (resolution_rate * 0.20),
            4,
        )
        operational_score = round((response_rate * 0.35) + (resolution_rate * 0.45) + (years_online_score * 0.20), 4)

        final_score = round(
            (reputation_score * 0.55) + (operational_score * 0.25) + (security_score * 0.20),
            4,
        )

        approved = (
            final_score >= 0.65
            and response_rate >= 0.65
            and resolution_rate >= 0.65
            and security_score >= 0.55
        )
        trust_label = self._classify_trust(final_score)
        risk_flags = self._build_risk_flags(domain, domain_match, response_rate, resolution_rate, final_score)
        reasons = self._build_reasons(
            baseline_name=baseline["display_name"],
            final_score=final_score,
            reputation_score=reputation_score,
            security_score=security_score,
            response_rate=response_rate,
            resolution_rate=resolution_rate,
            domain=domain,
            risk_flags=risk_flags,
        )

        return {
            "approved": approved,
            "score": final_score,
            "trust_label": trust_label,
            "rating": round(float(baseline["reclame_aqui_rating"]), 2),
            "trustpilot_rating": round(float(baseline["trustpilot_rating"]), 2),
            "response_rate": response_rate,
            "resolution_rate": resolution_rate,
            "years_online": int(baseline["years_online"]),
            "security_score": security_score,
            "reputation_score": reputation_score,
            "operational_score": operational_score,
            "domain_match_score": domain_match,
            "domain_reputation_score": domain_reputation,
            "domain": domain,
            "risk_flags": risk_flags,
            "reasons": reasons,
            "comment_summary": reasons[0],
        }

    def _normalize_store_name(self, store_name: str) -> str:
        lowered = store_name.lower().strip()
        return "".join(ch for ch in lowered if ch.isalnum())

    def _extract_domain(self, url: str) -> str:
        if not url:
            return ""
        parsed = urlparse(url)
        host = parsed.netloc.lower()
        if host.startswith("www."):
            host = host[4:]
        return host

    def _compute_domain_match_score(self, domain: str, official_domains: List[str], normalized_store: str) -> float:
        if not domain:
            return 0.0
        for official in official_domains:
            if domain == official or domain.endswith(f".{official}"):
                return 1.0

        if domain.endswith("google.com"):
            return 0.7

        if normalized_store and normalized_store in domain.replace(".", ""):
            return 0.65

        return 0.2

    def _compute_domain_reputation_score(self, domain: str) -> float:
        if not domain:
            return 0.0
        tld = domain.split(".")[-1]
        if tld in self._SUSPICIOUS_TLDS:
            return 0.2
        return 1.0

    def _classify_trust(self, score: float) -> str:
        if score >= 0.8:
            return "alta"
        if score >= 0.65:
            return "moderada"
        return "baixa"

    def _build_risk_flags(
        self,
        domain: str,
        domain_match: float,
        response_rate: float,
        resolution_rate: float,
        final_score: float,
    ) -> List[str]:
        flags: List[str] = []
        if domain_match < 0.5:
            flags.append("dominio_com_baixa_correspondencia_com_a_loja")
        if response_rate < 0.75:
            flags.append("baixa_taxa_de_resposta_a_reclamacoes")
        if resolution_rate < 0.70:
            flags.append("baixa_taxa_de_resolucao_de_reclamacoes")
        if domain and domain.split(".")[-1] in self._SUSPICIOUS_TLDS:
            flags.append("tld_suspeito")
        if final_score < 0.65:
            flags.append("score_geral_abaixo_do_limite")
        return flags

    def _build_reasons(
        self,
        baseline_name: str,
        final_score: float,
        reputation_score: float,
        security_score: float,
        response_rate: float,
        resolution_rate: float,
        domain: str,
        risk_flags: List[str],
    ) -> List[str]:
        reasons = [
            (
                f"Loja {baseline_name} com score de confianca {final_score:.2f} "
                f"(reputacao {reputation_score:.2f}, seguranca {security_score:.2f})."
            ),
            (
                f"Indicadores de atendimento: resposta {response_rate * 100:.0f}% "
                f"e resolucao {resolution_rate * 100:.0f}%."
            ),
            f"Dominio analisado: {domain or 'nao informado'}.",
        ]
        if risk_flags:
            reasons.append(f"Riscos identificados: {', '.join(risk_flags)}.")
        return reasons
