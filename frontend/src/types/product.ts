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
}

export interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    products?: Product[];
    timestamp: number;
}
