import React, { useRef, useEffect } from 'react';
import { Message } from '../types/product';
import MessageBubble from './MessageBubble';
import Loading from './Loading';

interface ChatContainerProps {
    messages: Message[];
    isLoading: boolean;
    onSuggestionClick: (suggestion: string) => void;
}

const suggestions = [
    'Melhores pre\u00e7os de iPhone 15',
    'Onde comprar PS5 com seguran\u00e7a?',
    'Fones bluetooth at\u00e9 R$500',
    'Monitor 4k mais bem avaliado',
];

const ChatContainer: React.FC<ChatContainerProps> = ({ messages, isLoading, onSuggestionClick }) => {
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages, isLoading]);

    return (
        <div ref={scrollRef} className="flex-1 overflow-y-auto mb-32">
            {messages.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center space-y-6 px-4">
                    <div className="w-16 h-16 bg-white/5 rounded-2xl flex items-center justify-center border border-white/10 shadow-inner">
                        <span className="text-2xl font-bold text-accent">SA</span>
                    </div>
                    <h1 className="text-3xl font-bold text-text-primary text-center">
                        Conte o produto que voc\u00ea quer comprar
                    </h1>
                    <p className="max-w-2xl text-center text-sm text-text-secondary leading-6">
                        O frontend envia sua busca para o backend, que aciona os agentes de descoberta,
                        confian\u00e7a e ranking para sugerir as melhores op\u00e7\u00f5es.
                    </p>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-xl w-full">
                        {suggestions.map((suggestion) => (
                            <button
                                key={suggestion}
                                type="button"
                                onClick={() => onSuggestionClick(suggestion)}
                                className="p-4 bg-white/5 border border-white/10 rounded-xl text-sm text-text-secondary text-center hover:bg-white/10 transition-colors cursor-pointer"
                            >
                                {suggestion}
                            </button>
                        ))}
                    </div>
                </div>
            ) : (
                <div className="flex flex-col">
                    {messages.map((m) => (
                        <MessageBubble key={m.id} message={m} />
                    ))}
                    {isLoading && (
                        <div className="w-full py-8 flex justify-center bg-white/[0.02]">
                            <div className="max-w-3xl w-full px-4">
                                <Loading />
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default ChatContainer;
