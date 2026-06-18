import { useState, useEffect } from 'react';
import { getAllClaims } from '../api/client';
import type { Claim } from '../api/client';
import { CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { BlurFade } from '@/components/ui/blur-fade';
import { MagicCard } from '@/components/ui/magic-card';
import { 
  Sparkles, 
  ChevronDown, 
  ChevronUp, 
  Quote,
  FileText,
  Filter
} from 'lucide-react';

export default function Claims() {
  const [claims, setClaims] = useState<Claim[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [filter, setFilter] = useState<'all' | 'finding' | 'hypothesis' | 'limitation'>('all');

  useEffect(() => {
    loadClaims();
  }, []);

  const loadClaims = async () => {
    setLoading(true);
    try {
      const data = await getAllClaims();
      setClaims(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Failed to load claims:', error);
      setClaims([]);
    }
    setLoading(false);
  };

  const filteredClaims = filter === 'all'
    ? claims
    : claims.filter(c => c.claim_type === filter);

  const stats = {
    findings: claims.filter(c => c.claim_type === 'finding').length,
    hypotheses: claims.filter(c => c.claim_type === 'hypothesis').length,
    limitations: claims.filter(c => c.claim_type === 'limitation').length,
    total: claims.length
  };

  const filterOptions: Array<'all' | 'finding' | 'hypothesis' | 'limitation'> = ['all', 'finding', 'hypothesis', 'limitation'];

  const getClaimBadgeStyle = (type: string) => {
    switch (type) {
      case 'finding':
        return 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20';
      case 'hypothesis':
        return 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20';
      default:
        return 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20';
    }
  };

  if (loading) {
    return (
      <div className="space-y-6 max-w-5xl mx-auto py-4 animate-pulse">
        <div className="h-10 bg-muted rounded w-1/3" />
        <div className="grid grid-cols-4 gap-3">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-20 bg-muted rounded-xl" />
          ))}
        </div>
        <div className="space-y-3 pt-6">
          {[1, 2, 3].map((i) => (
            <div key={i} className="border border-border/80 rounded-xl p-5 bg-card/30 h-16" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Title section */}
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-primary" />
          <span className="text-xs font-semibold uppercase tracking-wider text-primary/80">Extracted Claims Database</span>
        </div>
        <h1 className="text-4xl font-extrabold tracking-tight">Extracted Claims</h1>
        <p className="text-sm text-muted-foreground">
          Browse and filter claims extracted from all ingested literature, structured by semantic types.
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MagicCard mode="gradient" gradientColor="var(--muted)" className="border-border">
          <CardContent className="p-4 text-center space-y-1">
            <div className="text-2xl font-extrabold text-emerald-600 dark:text-emerald-400">{stats.findings}</div>
            <div className="text-[10px] text-muted-foreground uppercase font-semibold tracking-wider">Findings</div>
          </CardContent>
        </MagicCard>

        <MagicCard mode="gradient" gradientColor="var(--muted)" className="border-border">
          <CardContent className="p-4 text-center space-y-1">
            <div className="text-2xl font-extrabold text-amber-600 dark:text-amber-400">{stats.hypotheses}</div>
            <div className="text-[10px] text-muted-foreground uppercase font-semibold tracking-wider">Hypotheses</div>
          </CardContent>
        </MagicCard>

        <MagicCard mode="gradient" gradientColor="var(--muted)" className="border-border">
          <CardContent className="p-4 text-center space-y-1">
            <div className="text-2xl font-extrabold text-rose-600 dark:text-rose-400">{stats.limitations}</div>
            <div className="text-[10px] text-muted-foreground uppercase font-semibold tracking-wider">Limitations</div>
          </CardContent>
        </MagicCard>

        <MagicCard mode="gradient" gradientColor="var(--muted)" className="border-border">
          <CardContent className="p-4 text-center space-y-1">
            <div className="text-2xl font-extrabold text-primary">{stats.total}</div>
            <div className="text-[10px] text-muted-foreground uppercase font-semibold tracking-wider">Total Claims</div>
          </CardContent>
        </MagicCard>
      </div>

      {/* Filter Options */}
      <div className="flex items-center gap-3 bg-muted/30 p-1.5 rounded-xl border border-border/80 w-fit flex-wrap">
        <span className="text-xs text-muted-foreground px-2 flex items-center gap-1">
          <Filter className="h-3.5 w-3.5" />
          Filter:
        </span>
        {filterOptions.map((opt) => (
          <button
            key={opt}
            onClick={() => setFilter(opt)}
            className={`px-4 py-1.5 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all duration-200 ${
              filter === opt
                ? 'bg-background text-foreground shadow-sm border border-border/40'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            {opt}
          </button>
        ))}
      </div>

      {filteredClaims.length === 0 ? (
        <div className="text-center py-16 border border-dashed rounded-2xl bg-muted/[0.01]">
          <FileText className="h-12 w-12 text-muted-foreground/30 mx-auto mb-3" />
          <p className="text-sm text-muted-foreground">No claims match the filter selection.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredClaims.map((claim, idx) => {
            const isExpanded = expandedId === claim.id;
            return (
              <BlurFade key={claim.id} delay={idx * 0.02} inView>
                <div 
                  className={`border rounded-xl bg-card transition-all duration-300 ${
                    isExpanded ? 'border-primary' : 'border-border'
                  }`}
                >
                  <div
                    className="p-4 flex flex-col gap-3 cursor-pointer select-none"
                    onClick={() => setExpandedId(isExpanded ? null : claim.id)}
                  >
                    <div className="flex items-center gap-3 flex-wrap">
                      <Badge className={`text-[9px] uppercase font-semibold ${getClaimBadgeStyle(claim.claim_type)}`}>
                        {claim.claim_type}
                      </Badge>
                      <span className="text-xs font-semibold text-muted-foreground/80 font-mono">{claim.paper_id}</span>
                      <span className="text-xs text-muted-foreground/60">{claim.source_section}</span>
                      <div className="ml-auto flex items-center gap-3">
                        <span className="text-xs font-medium text-muted-foreground">
                          Confidence: {(claim.confidence * 100).toFixed(0)}%
                        </span>
                        <div className="text-muted-foreground">
                          {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                        </div>
                      </div>
                    </div>

                    <p className="text-sm leading-relaxed font-medium">
                      {isExpanded ? claim.text : (claim.text ?? '').slice(0, 150) + ((claim.text ?? '').length > 150 ? '...' : '')}
                    </p>

                    {isExpanded && (
                      <div className="border-t border-border pt-4 mt-1 space-y-3 text-xs text-muted-foreground">
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <strong>Page Number:</strong> {claim.page_number}
                          </div>
                          <div>
                            <strong>Validated:</strong> {claim.is_validated ? 'Yes' : 'No'}
                          </div>
                        </div>
                        <div className="bg-muted/30 rounded-lg p-3 border border-border/40 flex items-start gap-2.5">
                          <Quote className="h-4 w-4 text-muted-foreground/60 shrink-0 mt-0.5" />
                          <p className="italic leading-relaxed">
                            "{claim.source_sentence}"
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </BlurFade>
            );
          })}
        </div>
      )}
    </div>
  );
}