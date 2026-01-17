interface Opportunity {
  strike: number;
  expiry: string;
  premium: number;
  win_prob: number;
  delta: number;
  gamma: number;
  theta: number;
  vega: number;
  iv: number;
}

interface OpportunityTableProps {
  opportunities: Opportunity[];
  isLoading: boolean;
}

export default function OpportunityTable({ opportunities, isLoading }: OpportunityTableProps) {
  if (isLoading) {
    return (
      <div className="bg-black/20 border border-white/10 rounded-lg p-12 text-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-6 h-6 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
          <p className="text-gray-400 text-sm animate-pulse">
            System Scanning...
          </p>
        </div>
      </div>
    );
  }

  if (opportunities.length === 0) {
    return (
      <div className="bg-black/20 border border-white/10 rounded-lg p-12 text-center">
        <p className="text-gray-400 text-sm">
          No opportunities found with Win Prob &gt; 80%
        </p>
        <p className="text-gray-500 text-xs mt-2">
          Try a different ticker or check back later
        </p>
      </div>
    );
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  };

  const getWinProbColor = (prob: number) => {
    if (prob >= 0.80) return "text-emerald-400";
    if (prob >= 0.60) return "text-yellow-400";
    return "text-red-400";
  };

  const getDeltaIndicator = (delta: number) => {
    const absDelta = Math.abs(delta);
    if (absDelta >= 0.25) return "w-2 h-2 bg-white rounded-full";
    if (absDelta >= 0.15) return "w-1.5 h-1.5 bg-white/60 rounded-full";
    return "w-1 h-1 bg-white/30 rounded-full";
  };

  return (
    <div className="bg-black/20 border border-white/10 rounded-lg overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-white/10 bg-black/20">
              <th className="text-left p-3 text-gray-400 font-semibold">Strike</th>
              <th className="text-left p-3 text-gray-400 font-semibold">Exp</th>
              <th className="text-right p-3 text-gray-400 font-semibold">Premium</th>
              <th className="text-right p-3 text-gray-400 font-semibold">Win Prob</th>
              <th className="text-right p-3 text-gray-400 font-semibold">Delta</th>
              <th className="text-right p-3 text-gray-400 font-semibold">IV</th>
            </tr>
          </thead>
          <tbody>
            {opportunities.map((opp, idx) => {
              const winProbPercent = opp.win_prob;
              const rowClasses = `border-b border-white/5 hover:bg-white/5 transition-colors`;
              
              return (
                <tr key={idx} className={rowClasses}>
                  <td className="p-3 text-white font-bold">
                    ${opp.strike.toFixed(2)}
                  </td>
                  <td className="p-3 text-gray-400">
                    {formatDate(opp.expiry)}
                  </td>
                  <td className="p-3 text-right text-white font-mono">
                    ${opp.premium.toFixed(2)}
                  </td>
                  <td className="p-3 text-right">
                    <span className={`font-bold text-sm ${getWinProbColor(winProbPercent)}`}>
                      {(winProbPercent * 100).toFixed(1)}%
                    </span>
                  </td>
                  <td className="p-3 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <span className="text-gray-400 font-mono text-xs">
                        {opp.delta.toFixed(4)}
                      </span>
                      <div className={getDeltaIndicator(opp.delta)}></div>
                    </div>
                  </td>
                  <td className="p-3 text-right text-gray-400 font-mono text-xs">
                    {(opp.iv * 100).toFixed(1)}%
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
