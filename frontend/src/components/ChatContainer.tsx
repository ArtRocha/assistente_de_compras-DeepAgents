import React, { useRef, useEffect } from 'react';
import { Message } from '../types/product';
import MessageBubble from './MessageBubble';
import Loading from './Loading';

interface ChatContainerProps {
    messages: Message[];
    isLoading: boolean;
}

const ChatContainer: React.FC<ChatContainerProps> = ({ messages, isLoading }) => {
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
                        <span className="text-2xl font-bold text-accent">🛒</span>
                    </div>
                    <h1 className="text-3xl font-bold text-text-primary text-center">
                        Como posso ajudar na sua compra hoje?
                    </h1>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-xl w-full">
                        {["Melhores preços de iPhone 15", "Onde comprar PS5 com segurança?", "Fones bluetooth até R$500", "Monitor 4k mais bem avaliado"].map((suggestion) => (
                            <div key={suggestion} className="p-4 bg-white/5 border border-white/10 rounded-xl text-sm text-text-secondary text-center hover:bg-white/10 transition-colors cursor-pointer">
                                {suggestion}
                            </div>
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
