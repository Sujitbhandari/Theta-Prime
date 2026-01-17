interface TickerSearchProps {
  value: string;
  onChange: (value: string) => void;
  onSearch: () => void;
  isLoading: boolean;
}

export default function TickerSearch({ value, onChange, onSearch, isLoading }: TickerSearchProps) {
  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !isLoading && value.trim()) {
      onSearch();
    }
  };

  return (
    <div className="flex gap-3 items-stretch">
      <div className="relative flex-1">
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value.toUpperCase().replace(/[^A-Z-]/g, ""))}
          onKeyPress={handleKeyPress}
          placeholder="Enter ticker (e.g., NVDA, TSLA, AAPL)"
          className="w-full px-4 py-3 bg-black/20 border border-white/10 text-white font-mono rounded-lg focus:outline-none focus:border-white/30 focus:ring-1 focus:ring-white/20 transition-all placeholder:text-gray-500"
          disabled={isLoading}
          maxLength={10}
        />
        <span className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 text-sm font-bold pointer-events-none">
          $
        </span>
      </div>
      <button
        onClick={onSearch}
        disabled={isLoading || !value.trim()}
        className="px-6 py-3 bg-white/10 hover:bg-white/20 disabled:bg-white/5 disabled:cursor-not-allowed text-white font-mono font-bold rounded-lg transition-all border border-white/10 hover:border-white/20 disabled:border-white/5 active:scale-95"
      >
        {isLoading ? (
          <span className="flex items-center gap-2">
            <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
            SCANNING
          </span>
        ) : (
          "SCAN"
        )}
      </button>
    </div>
  );
}
