import React from 'react';
import { ExternalLink, ShieldCheck, TrendingUp } from 'lucide-react';
import { Product } from '../types/product';

interface ProductCardProps {
    product: Product;
}

const ProductCard: React.FC<ProductCardProps> = ({ product }) => {
    const trustColor = product.trust_score > 0.8 ? 'text-accent' : 'text-yellow-500';
    const responseRate = product.response_rate ? Math.round(product.response_rate * 100) : null;
    const resolutionRate = product.resolution_rate ? Math.round(product.resolution_rate * 100) : null;

    return (
        <div className="flex flex-col bg-surface border border-border rounded-xl p-4 hover:border-accent/40 transition-all group">
            <div className="flex-1">
                <div className="flex justify-between items-start mb-2">
                    <span className="text-xs font-medium text-text-secondary uppercase tracking-wider">{product.store}</span>
                    <div className="flex items-center gap-1">
                        <TrendingUp size={14} className="text-accent" />
                        <span className="text-xs font-bold text-accent">{Math.round(product.final_score * 100)}% Score</span>
                    </div>
                </div>
                <h3 className="text-base font-semibold text-text-primary line-clamp-2 mb-3 leading-snug group-hover:text-accent transition-colors">
                    {product.title}
                </h3>
                {product.review_summary && (
                    <p className="text-sm text-text-secondary leading-6 mb-4">
                        {product.review_summary}
                    </p>
                )}
            </div>

            <div className="mt-auto">
                <div className="flex items-center justify-between mb-4">
                    <div className="flex flex-col">
                        <span className="text-xl font-bold text-text-primary">
                            R$ {product.price.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                        </span>
                    </div>
                    <div className="flex items-center gap-1.5 px-2 py-1 bg-white/5 rounded-md">
                        <ShieldCheck size={14} className={trustColor} />
                        <span className={`text-xs font-medium ${trustColor}`}>
                            {Math.round(product.trust_score * 100)}% Confianca
                        </span>
                    </div>
                </div>
                {(responseRate !== null || resolutionRate !== null) && (
                    <div className="mb-4 grid grid-cols-2 gap-2 text-xs text-text-secondary">
                        <div className="rounded-lg bg-white/5 px-3 py-2">
                            Respostas: {responseRate ?? '-'}%
                        </div>
                        <div className="rounded-lg bg-white/5 px-3 py-2">
                            Solucao: {resolutionRate ?? '-'}%
                        </div>
                    </div>
                )}

                <a
                    href={product.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center justify-center gap-2 w-full py-2.5 bg-white/5 hover:bg-accent text-text-primary hover:text-white rounded-lg font-medium transition-all"
                >
                    Ver produto
                    <ExternalLink size={16} />
                </a>
            </div>
        </div>
    );
};

export default ProductCard;
