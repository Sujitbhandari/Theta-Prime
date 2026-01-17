"use client";

import { useState, useEffect } from "react";
import RegimeBadge from "@/components/RegimeBadge";
import TickerSearch from "@/components/TickerSearch";
import OpportunityTable from "@/components/OpportunityTable";
import StatsPanel from "@/components/StatsPanel";

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

interface ScanData {
  ticker: string;
  market_status: string;
  crash_probability?: number;
  safety_score?: number;
  vix?: number;
  opportunities: Opportunity[];
  spot_price?: number;
  expiry?: string;
}

export default function Home() {
  const [ticker, setTicker] = useState("NVDA");
  const [isLoading, setIsLoading] = useState(false);
  const [data, setData] = useState<ScanData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async (searchTicker: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const scanResponse = await fetch(`http://127.0.0.1:8000/api/scan/${searchTicker}`);
      
      if (!scanResponse.ok) {
        throw new Error(`HTTP error! status: ${scanResponse.status}`);
      }
      
      const result = await scanResponse.json();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch data");
      setData(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData(ticker);
  }, []);

  const handleSearch = () => {
    if (ticker.trim()) {
      fetchData(ticker.trim());
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900 text-white font-mono">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-6 max-w-[1800px]">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
          <div className="lg:col-span-2">
            <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-xl p-4">
              <TickerSearch
                value={ticker}
                onChange={setTicker}
                onSearch={handleSearch}
                isLoading={isLoading}
              />
            </div>
          </div>
          <div className="lg:col-span-1">
            {data ? (
              <RegimeBadge 
                status={data.market_status} 
                crashProbability={data.crash_probability}
                vix={data.vix}
              />
            ) : (
              <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-xl p-4 h-full flex items-center justify-center">
                <span className="text-gray-400 text-sm">Waiting for market data...</span>
              </div>
            )}
          </div>
        </div>

        {data && data.spot_price && (
          <div className="mb-6 flex flex-wrap items-center gap-4 text-sm text-gray-400">
            <div className="flex items-center gap-2">
              <span className="text-gray-400">Spot Price:</span>
              <span className="text-white font-bold">${data.spot_price.toFixed(2)}</span>
            </div>
            {data.expiry && (
              <>
                <span className="text-gray-600">|</span>
                <div className="flex items-center gap-2">
                  <span className="text-gray-400">Expiry:</span>
                  <span className="text-white">{new Date(data.expiry).toLocaleDateString()}</span>
                </div>
              </>
            )}
            {data.safety_score !== undefined && (
              <>
                <span className="text-gray-600">|</span>
                <div className="flex items-center gap-2">
                  <span className="text-gray-400">Safety Score:</span>
                  <span className="text-white">{data.safety_score.toFixed(1)}%</span>
                </div>
              </>
            )}
          </div>
        )}

        {error && (
          <div className="mb-6 p-4 bg-white/5 backdrop-blur-md border border-red-500/20 rounded-xl text-red-400">
            <div className="flex items-center gap-2">
              <span>Error: {error}</span>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 mb-8">
          <div className="xl:col-span-2">
            <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-xl p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-bold text-white">
                  Market Analytics
                </h2>
                <span className="text-xs text-gray-400">{ticker}</span>
              </div>
              <StatsPanel
                ticker={ticker}
                spotPrice={data?.spot_price}
                expiry={data?.expiry}
                opportunities={data?.opportunities}
                vix={data?.vix}
                safetyScore={data?.safety_score}
              />
            </div>
          </div>

          <div className="xl:col-span-1">
            <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-xl p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-bold text-white">
                  Put Opportunities
                </h2>
                <span className="text-xs text-gray-400">Win Prob &gt; 80%</span>
              </div>
              <OpportunityTable
                opportunities={data?.opportunities || []}
                isLoading={isLoading}
              />
              
              {data && data.opportunities.length > 0 && (
                <div className="mt-4 pt-4 border-t border-white/10 text-xs text-gray-400 text-center">
                  {data.opportunities.length} opportunity{data.opportunities.length !== 1 ? "ies" : "y"} found
                </div>
              )}
            </div>
          </div>
        </div>

        <footer className="mt-8 pt-6 border-t border-white/10 text-center">
          <p className="text-gray-400 text-xs">
            Theta-Prime Analytics Platform - C++ Engine + VIX Risk Management
          </p>
        </footer>
      </div>
    </div>
  );
}
