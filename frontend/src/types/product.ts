export interface Product {
    title: string;
    price: number;
    store: string;
    url: string;
    trust_score: number;
    final_score: number;
}

export interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    products?: Product[];
    timestamp: number;
}
