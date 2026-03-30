import React, { useState } from 'react';
import ChatContainer from './components/ChatContainer';
import InputBox from './components/InputBox';
import { Message } from './types/product';
import { searchProducts } from './services/api';

const App: React.FC = () => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [isLoading, setIsLoading] = useState(false);

    const handleSendMessage = async (content: string) => {
        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content,
            timestamp: Date.now(),
        };

        setMessages((prev) => [...prev, userMessage]);
        setIsLoading(true);

        try {
            const results = await searchProducts(content);

            const assistantMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: results.length > 0
                    ? `Encontrei ${results.length} opções para você com base no preço e na confiabilidade das lojas:`
                    : "Desculpe, não conseguimos encontrar produtos que correspondam à sua pesquisa no momento.",
                products: results,
                timestamp: Date.now(),
            };

            setMessages((prev) => [...prev, assistantMessage]);
        } catch (error) {
            const errorMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: "Ocorreu um erro ao processar sua solicitação. Por favor, tente novamente.",
                timestamp: Date.now(),
            };
            setMessages((prev) => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-screen bg-background">
            <header className="fixed top-0 left-0 right-0 h-16 border-b border-border bg-background/80 backdrop-blur-md z-50 flex items-center justify-between px-6">
                <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-accent rounded-lg flex items-center justify-center font-bold text-white shadow-lg">S</div>
                    <span className="font-semibold text-text-primary tracking-tight">Shopping Assistant <span className="text-accent underline underline-offset-4 decoration-2">Pro</span></span>
                </div>
                <div className="flex gap-4">
                    <div className="px-3 py-1 bg-white/5 border border-white/10 rounded-full text-xs font-medium text-text-secondary">GPT-4o + MultiAgents</div>
                </div>
            </header>

            <main className="flex-1 flex flex-col pt-16">
                <ChatContainer messages={messages} isLoading={isLoading} />
                <InputBox onSend={handleSendMessage} isLoading={isLoading} />
            </main>
        </div>
    );
};

export default App;
