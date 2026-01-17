interface RegimeBadgeProps {
  status: string;
  crashProbability?: number;
  vix?: number;
}

export default function RegimeBadge({ status, crashProbability, vix }: RegimeBadgeProps) {
  const isSafe = status === "Safe";
  const isCaution = status === "Caution";
  const isDanger = status === "Danger";

  if (isSafe) {
    return (
      <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-xl p-4 h-full flex flex-col items-center justify-center">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-2.5 h-2.5 bg-emerald-400 rounded-full animate-pulse shadow-lg shadow-emerald-400/50"></div>
          <span className="text-emerald-400 font-mono text-sm font-bold">MARKET SAFE</span>
        </div>
        {vix !== undefined && vix !== null && (
          <span className="text-xs text-gray-400 font-mono">VIX: {vix.toFixed(1)}</span>
        )}
      </div>
    );
  }

  if (isCaution) {
    return (
      <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-xl p-4 h-full flex flex-col items-center justify-center">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-2.5 h-2.5 bg-yellow-400 rounded-full animate-pulse shadow-lg shadow-yellow-400/50"></div>
          <span className="text-yellow-400 font-mono text-sm font-bold">MARKET CAUTION</span>
        </div>
        {vix !== undefined && vix !== null && (
          <span className="text-xs text-gray-400 font-mono">VIX: {vix.toFixed(1)}</span>
        )}
      </div>
    );
  }

  return (
    <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-xl p-4 h-full flex flex-col items-center justify-center">
      <div className="flex items-center gap-3 mb-2">
        <div className="w-2.5 h-2.5 bg-red-400 rounded-full animate-pulse shadow-lg shadow-red-400/50"></div>
        <span className="text-red-400 font-mono text-sm font-bold">MARKET DANGER</span>
      </div>
      {vix !== undefined && vix !== null && (
        <span className="text-xs text-gray-400 font-mono">VIX: {vix.toFixed(1)}</span>
      )}
    </div>
  );
}
