import { Product } from '../types/product';

export const searchProducts = async (query: string): Promise<Product[]> => {
    try {
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query }),
        });

        if (!response.ok) {
            throw new Error('Search failed');
        }

        return await response.ok ? response.json() : [];
    } catch (error) {
        console.error('API Error:', error);
        // Return mock data if API is not available for local testing
        return [
            {
                title: "Mock iPhone 13",
                price: 4999.99,
                store: "Store Mock",
                url: "#",
                trust_score: 0.95,
                final_score: 0.92
            }
        ];
    }
};
