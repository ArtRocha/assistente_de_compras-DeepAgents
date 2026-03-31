import { Product } from '../types/product';

export const searchProducts = async (query: string): Promise<Product[]> => {
    const response = await fetch('/api/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
    });

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || 'Search failed');
    }

    return response.json();
};
