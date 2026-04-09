export interface Product {
    title: string;
    price: number;
    store: string;
    url: string;
    trust_score: number;
    final_score: number;
    source?: string;
    integrity_verified?: boolean;
    response_rate?: number;
    resolution_rate?: number;
    review_summary?: string;
    trust_label?: string;
    trust_reasons?: string[];
    trust_metrics?: Record<string, unknown>;
}

export interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    products?: Product[];
    timestamp: number;
}
