import json
from pathlib import Path
from typing import List

from ..schemas.product import Product
from ..services.scoring import ScoringEngine
from ..llm.client import get_llm

_PROMPT_PATH = Path(__file__).resolve().parent.parent / "config" / "prompts" / "ranking.txt"


class RankingAgent:
    """Ordena ofertas aprovadas e gera recomendação de compra.

    Com Ollama disponível: o LLM escreve uma recomendação personalizada para o
    consumidor explicando qual produto escolher e por quê.
    Sem Ollama: apenas ordena por score matemático (comportamento original).
    """

    def __init__(self):
        self._prompt_template = _PROMPT_PATH.read_text(encoding="utf-8")

    async def run(self, products: List[Product], query: str = "") -> List[Product]:
        print(f"[RankingAgent] Ordenando {len(products)} ofertas aprovadas...")

        scored = ScoringEngine.compute_scores(products)
        ranked = ScoringEngine.rank_products(scored)

        print("[RankingAgent] Ordenação matemática concluída.")

        # --- LLM: gerar recomendação final ---
        llm = get_llm()
        if llm and ranked:
            try:
                products_summary = json.dumps(
                    [
                        {
                            "titulo": p.title,
                            "preco": f"R$ {p.price:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                            "loja": p.store,
                            "score_confianca": round(p.trust_score or 0, 2),
                            "score_final": round(p.final_score or 0, 2),
                            "aprovada": p.integrity_verified,
                        }
                        for p in ranked
                    ],
                    ensure_ascii=False,
                    indent=2,
                )
                prompt = self._prompt_template.format(
                    query=query or "produto buscado",
                    products=products_summary,
                )
                response = llm.invoke(prompt)
                recommendation = response.content if hasattr(response, "content") else str(response)
                recommendation = recommendation.strip()
                print(f"[RankingAgent][LLM] Recomendação gerada:\n{recommendation}\n")

                # Anexa a recomendação ao primeiro produto (melhor oferta)
                if ranked:
                    ranked[0].review_summary = (
                        f"[Recomendação do Agente] {recommendation}\n\n"
                        f"[Análise da Loja] {ranked[0].review_summary or ''}"
                    ).strip()
            except Exception as e:
                print(f"[RankingAgent][LLM] ERRO ao gerar recomendação: {e} — retornando ranking sem LLM.")

        print(f"[RankingAgent] Pipeline finalizado com {len(ranked)} produtos.")
        return ranked

    # Compatibilidade com o OrchestratorAgent que não passa query
    async def _run_compat(self, products: List[Product]) -> List[Product]:
        return await self.run(products, query="")
