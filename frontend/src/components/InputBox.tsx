import React, { useState, useRef, useEffect } from 'react';
import { ArrowUp } from 'lucide-react';

interface InputBoxProps {
    onSend: (message: string) => void;
    isLoading: boolean;
}

const InputBox: React.FC<InputBoxProps> = ({ onSend, isLoading }) => {
    const [input, setInput] = useState('');
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const handleSubmit = (e?: React.FormEvent) => {
        e?.preventDefault();
        if (input.trim() && !isLoading) {
            onSend(input);
            setInput('');
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
        }
    };

    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
        }
    }, [input]);

    return (
        <div className="fixed bottom-0 left-0 right-0 p-4 md:p-8 bg-gradient-to-t from-background via-background/90 to-transparent">
            <div className="max-w-3xl mx-auto relative group">
                <form onSubmit={handleSubmit} className="relative">
                    <textarea
                        ref={textareaRef}
                        rows={1}
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Pergunte ao assistente (ex: quero comprar um iPhone 13)"
                        className="w-full bg-surface border border-border focus:border-accent/50 outline-none rounded-2xl py-4 pl-4 pr-14 resize-none max-h-48 text-text-primary placeholder:text-text-secondary transition-all shadow-xl"
                    />
                    <button
                        type="submit"
                        disabled={!input.trim() || isLoading}
                        className="absolute right-3 bottom-3 p-2 bg-accent disabled:bg-white/10 text-white rounded-xl transition-all hover:bg-accent-hover disabled:cursor-not-allowed group-focus-within:scale-105"
                    >
                        <ArrowUp size={20} strokeWidth={3} />
                    </button>
                </form>
                <p className="text-[10px] text-center mt-3 text-text-secondary uppercase tracking-[0.2em] font-medium opacity-50">
                    Powered by Multi-Agent Shopping Intelligence
                </p>
            </div>
        </div>
    );
};

export default InputBox;
