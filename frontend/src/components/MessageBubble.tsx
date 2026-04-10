import React from 'react';
import { User, Bot } from 'lucide-react';
import { Message } from '../types/product';
import ProductCard from './ProductCard';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

interface MessageBubbleProps {
    message: Message;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
    const isUser = message.role === 'user';

    return (
        <div className={cn(
            "w-full py-8 flex justify-center",
            !isUser && "bg-white/[0.02]"
        )}>
            <div className="max-w-3xl w-full flex gap-6 px-4">
                <div className={cn(
                    "h-8 w-8 rounded flex items-center justify-center shrink-0 mt-1",
                    isUser ? "bg-accent" : "bg-[#19c37d]"
                )}>
                    {isUser ? <User size={20} className="text-white" /> : <Bot size={20} className="text-white" />}
                </div>

                <div className="flex-1 space-y-4">
                    <div className="text-text-primary leading-7 whitespace-pre-wrap">
                        {message.content}
                    </div>

                    {message.products && message.products.length > 0 && (
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-6">
                            {message.products.map((product, idx) => (
                                <ProductCard key={idx} product={product} />
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default MessageBubble;
