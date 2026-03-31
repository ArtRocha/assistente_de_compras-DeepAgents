import React, { useState } from 'react';
import ChatContainer from './components/ChatContainer';
import InputBox from './components/InputBox';
import { Message } from './types/product';
import { searchProducts } from './services/api';

const App: React.FC = () => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [lastQuery, setLastQuery] = useState('');

    const handleSendMessage = async (content: string) => {
        const normalizedContent = content.trim();
        if (!normalizedContent || isLoading) {
            return;
        }

        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: normalizedContent,
            timestamp: Date.now(),
        };

        setMessages((prev) => [...prev, userMessage]);
        setIsLoading(true);
        setLastQuery(normalizedContent);

        try {
            const results = await searchProducts(normalizedContent);

            const assistantMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: results.length > 0
                    ? `Os agentes encontraram ${results.length} op\u00e7\u00f5es confi\u00e1veis para "${normalizedContent}", j\u00e1 ordenadas do menor pre\u00e7o para o maior.`
                    : `Os agentes n\u00e3o encontraram resultados relevantes para "${normalizedContent}" no momento.`,
                products: results,
                timestamp: Date.now(),
            };

            setMessages((prev) => [...prev, assistantMessage]);
        } catch (error) {
            const message = error instanceof Error ? error.message : 'Erro desconhecido';
            const errorMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: `N\u00e3o consegui consultar o backend agora. Verifique se a API FastAPI est\u00e1 rodando na porta 8000. Detalhe: ${message}`,
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
                    <div className="px-3 py-1 bg-white/5 border border-white/10 rounded-full text-xs font-medium text-text-secondary">Frontend + FastAPI + MultiAgents</div>
                </div>
            </header>

            <main className="flex-1 flex flex-col pt-16">
                <section className="px-4 md:px-6 pt-6">
                    <div className="max-w-3xl mx-auto rounded-2xl border border-border bg-surface/60 backdrop-blur px-4 py-3 text-sm text-text-secondary">
                        {isLoading
                            ? `Consultando os agentes para: "${lastQuery}"`
                            : 'Digite o produto desejado para o frontend acionar os agentes de compra no backend.'}
                    </div>
                </section>
                <ChatContainer
                    messages={messages}
                    isLoading={isLoading}
                    onSuggestionClick={handleSendMessage}
                />
                <InputBox onSend={handleSendMessage} isLoading={isLoading} />
            </main>
        </div>
    );
};

export default App;
