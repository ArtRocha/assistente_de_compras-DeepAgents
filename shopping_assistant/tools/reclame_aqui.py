import asyncio
from typing import Dict


class ReclameAquiTool:
    """Simulates store reputation checks inspired by Reclame Aqui signals."""

    async def get_store_trust(self, store_name: str) -> Dict[str, float | str | bool]:
        await asyncio.sleep(0.3)

        trust_db = {
            "Amazon": {
                "rating": 8.8,
                "response_rate": 0.98,
                "resolution_rate": 0.93,
                "comment_summary": "Loja responde rapidamente e costuma resolver a maioria dos problemas relatados.",
            },
            "Mercado Livre": {
                "rating": 7.4,
                "response_rate": 0.87,
                "resolution_rate": 0.79,
                "comment_summary": "Bom volume de respostas, mas a qualidade da resolução varia conforme o vendedor.",
            },
            "Magalu": {
                "rating": 9.1,
                "response_rate": 0.99,
                "resolution_rate": 0.95,
                "comment_summary": "Alta confiança geral, com bom histórico de atendimento e solução de reclamações.",
            },
            "Fast Shop": {
                "rating": 8.7,
                "response_rate": 0.96,
                "resolution_rate": 0.91,
                "comment_summary": "Boa reputação e bom retorno aos consumidores.",
            },
            "Kabum": {
                "rating": 8.4,
                "response_rate": 0.95,
                "resolution_rate": 0.88,
                "comment_summary": "Responde com frequência e mantém bom índice de solução.",
            },
            "Casas Bahia": {
                "rating": 8.0,
                "response_rate": 0.91,
                "resolution_rate": 0.82,
                "comment_summary": "Atende boa parte das reclamações e demonstra esforço razoável na resolução.",
            },
            "Ponto": {
                "rating": 6.4,
                "response_rate": 0.74,
                "resolution_rate": 0.61,
                "comment_summary": "Responde com menor consistência e acumula feedback misto sobre a resolução.",
            },
            "Olx": {
                "rating": 5.9,
                "response_rate": 0.70,
                "resolution_rate": 0.58,
                "comment_summary": "Muitos relatos dependem do vendedor e a confiança percebida é menor.",
            },
        }

        data = trust_db.get(
            store_name,
            {
                "rating": 5.5,
                "response_rate": 0.60,
                "resolution_rate": 0.55,
                "comment_summary": "Pouca informação consolidada sobre a reputação desta loja.",
            },
        )

        score = (
            (data["rating"] / 10.0) * 0.4
            + data["response_rate"] * 0.3
            + data["resolution_rate"] * 0.3
        )
        approved = (
            data["rating"] >= 7.0
            and data["response_rate"] >= 0.80
            and data["resolution_rate"] >= 0.75
        )

        return {
            "rating": data["rating"],
            "response_rate": data["response_rate"],
            "resolution_rate": data["resolution_rate"],
            "score": round(score, 4),
            "approved": approved,
            "comment_summary": data["comment_summary"],
        }
