import React from 'react';

const Loading: React.FC = () => {
    return (
        <div className="flex flex-col space-y-4 w-full p-4 animate-pulse">
            <div className="h-4 bg-white/5 rounded w-3/4"></div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {[1, 2].map((i) => (
                    <div key={i} className="h-48 bg-white/5 rounded-xl border border-white/10"></div>
                ))}
            </div>
        </div>
    );
};

export default Loading;
