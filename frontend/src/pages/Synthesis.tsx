import { useState, useEffect } from 'react';
import { getSynthesis } from '../api/client';
import type { SynthesisResult } from '../api/client';
import { Card, CardContent } from '@/components/ui/card';
import { ShinyButton } from '@/components/ui/shiny-button';
import { Badge } from '@/components/ui/badge';
import { BlurFade } from '@/components/ui/blur-fade';
import { MagicCard } from '@/components/ui/magic-card';
import { 
  Sparkles, 
  FileText, 
  CheckCircle2, 
  AlertTriangle, 
  HelpCircle, 
  Layers, 
  ChevronDown, 
  ChevronUp, 
  Loader2, 
  TrendingUp, 
  GitMerge, 
  AlertCircle 
} from 'lucide-react';

const LOADING_STEPS = [
  "Accessing SQLite database...",
  "Loading paper claims data...",
  "Running topic clustering...",
  "Performing cross-source semantic comparisons...",
  "Analyzing agreement ratios and contradictions...",
  "Generating final synthesis report..."
];

const SkeletonCard = () => (
  <div className="border border-border rounded-xl p-5 space-y-4 animate-pulse bg-card/30">
    <div className="flex justify-between items-center">
      <div className="h-5 bg-muted rounded w-2/3" />
      <div className="h-5 bg-muted rounded-full w-16" />
    </div>
    <div className="flex gap-3">
      <div className="h-4 bg-muted rounded w-12" />
      <div className="h-4 bg-muted rounded w-24" />
    </div>
    <div className="space-y-2 pt-2">
      <div className="h-3 bg-muted rounded w-full" />
      <div className="h-3 bg-muted rounded w-5/6" />
    </div>
  </div>
);

export default function Synthesis() {
  const [synthesis, setSynthesis] = useState<SynthesisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [expandedTopic, setExpandedTopic] = useState<string | null>(null);
  const [loadingStep, setLoadingStep] = useState(0);

  useEffect(() => {
    loadSynthesis();
  }, []);

  useEffect(() => {
    if (!loading) return;
    const interval = setInterval(() => {
      setLoadingStep((prev) => (prev + 1) % LOADING_STEPS.length);
    }, 2500);
    return () => clearInterval(interval);
  }, [loading]);

  const loadSynthesis = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await getSynthesis();
      if (data.success) {
        setSynthesis(data.synthesis);
      } else {
        setError(data.message);
      }
    } catch (err) {
      console.error('Failed to load synthesis:', err);
      setError('Failed to load synthesis. Make sure the backend is running and claims are extracted.');
    }
    setLoading(false);
  };

  const getConsensusBadgeStyle = (strength: string) => {
    switch (strength) {
      case 'strong': 
        return 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20';
      case 'moderate': 
        return 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20';
      default: 
        return 'bg-zinc-500/10 text-zinc-600 dark:text-zinc-400 border border-zinc-500/20';
    }
  };

  const getClaimTypeStyle = (type: string) => {
    switch (type) {
      case 'finding':
        return 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20';
      case 'hypothesis':
        return 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20';
      default:
        return 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20';
    }
  };

  const getRelationTypeStyle = (type: string) => {
    switch (type) {
      case 'agrees':
        return 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20';
      case 'contradicts':
        return 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20';
      case 'supports':
        return 'bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-500/20';
      default:
        return 'bg-zinc-500/10 text-zinc-600 dark:text-zinc-400 border border-zinc-500/20';
    }
  };

  if (loading) {
    return (
      <div className="space-y-8 max-w-5xl mx-auto py-4">
        {/* Header Skeleton */}
        <div className="space-y-3">
          <div className="h-10 bg-muted rounded w-1/3 animate-pulse" />
          <div className="h-5 bg-muted rounded w-1/2 animate-pulse" />
        </div>

        {/* Loading status panel */}
        <Card className="border border-border bg-card/50 overflow-hidden relative">
          <div className="absolute top-0 left-0 right-0 h-1 bg-muted overflow-hidden">
            <div className="h-full bg-primary animate-infinite-loading w-1/3 rounded-full" />
          </div>
          <CardContent className="p-8 flex flex-col items-center justify-center text-center space-y-4">
            <Loader2 className="h-8 w-8 text-primary animate-spin" />
            <div className="space-y-1">
              <h3 className="font-semibold text-lg">Synthesizing Claims</h3>
              <p className="text-sm text-muted-foreground min-h-[20px] transition-all duration-300">
                {LOADING_STEPS[loadingStep]}
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Shimmering grid of skeleton cards */}
        <div className="space-y-4">
          <div className="h-6 bg-muted rounded w-1/4 animate-pulse" />
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6 max-w-4xl mx-auto py-8">
        <h1 className="text-3xl font-bold tracking-tight">Cross-Source Synthesis</h1>
        <div className="bg-destructive/5 text-destructive border border-destructive/20 rounded-xl p-8 flex flex-col items-center gap-4 text-center">
          <AlertCircle className="h-10 w-10 text-destructive" />
          <div className="space-y-1">
            <h3 className="font-semibold text-lg">Failed to Load Synthesis</h3>
            <p className="text-sm text-muted-foreground max-w-md">{error}</p>
          </div>
          <ShinyButton onClick={loadSynthesis} className="mt-2">Retry Synthesis</ShinyButton>
        </div>
      </div>
    );
  }

  if (!synthesis) {
    return (
      <div className="text-center text-muted-foreground py-16 space-y-4">
        <GitMerge className="h-12 w-12 text-muted-foreground/50 mx-auto" />
        <p className="text-lg">No synthesis data available.</p>
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Title section */}
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-primary" />
          <span className="text-xs font-semibold uppercase tracking-wider text-primary/80">Cross-Source Synthesis</span>
        </div>
        <h1 className="text-4xl font-extrabold tracking-tight">Literature Synthesis</h1>
        <p className="text-sm text-muted-foreground">
          Aggregated findings across all ingested papers, grouped into logical topic clusters.
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <MagicCard mode="gradient" gradientColor="var(--muted)" className="border-border">
          <CardContent className="p-6 text-center space-y-1">
            <FileText className="h-5 w-5 text-muted-foreground mx-auto mb-2" />
            <div className="text-3xl font-extrabold tracking-tight">{synthesis.total_papers}</div>
            <div className="text-xs text-muted-foreground uppercase font-semibold tracking-wider">Papers Analyzed</div>
          </CardContent>
        </MagicCard>

        <MagicCard mode="gradient" gradientColor="var(--muted)" className="border-border">
          <CardContent className="p-6 text-center space-y-1">
            <Layers className="h-5 w-5 text-muted-foreground mx-auto mb-2" />
            <div className="text-3xl font-extrabold tracking-tight">{synthesis.total_claims}</div>
            <div className="text-xs text-muted-foreground uppercase font-semibold tracking-wider">Extracted Claims</div>
          </CardContent>
        </MagicCard>

        <MagicCard mode="gradient" gradientColor="var(--muted)" className="border-border">
          <CardContent className="p-6 text-center space-y-1">
            <GitMerge className="h-5 w-5 text-muted-foreground mx-auto mb-2" />
            <div className="text-3xl font-extrabold tracking-tight">{synthesis.topics.length}</div>
            <div className="text-xs text-muted-foreground uppercase font-semibold tracking-wider">Topic Clusters</div>
          </CardContent>
        </MagicCard>
      </div>

      {/* Overview Panels */}
      <div className="grid grid-cols-1 gap-4">
        {synthesis.areas_of_consensus.length > 0 && (
          <BlurFade delay={0.05} inView>
            <div className="border border-border/80 rounded-xl p-5 border-l-4 border-l-emerald-500 bg-emerald-500/[0.02] flex items-start gap-4">
              <CheckCircle2 className="h-5 w-5 text-emerald-600 dark:text-emerald-400 shrink-0 mt-0.5" />
              <div className="space-y-2">
                <h3 className="font-semibold text-sm text-emerald-800 dark:text-emerald-400">Areas of Consensus</h3>
                <ul className="space-y-1.5">
                  {synthesis.areas_of_consensus.map((item, idx) => (
                    <li key={idx} className="text-sm text-muted-foreground leading-relaxed">
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </BlurFade>
        )}

        {synthesis.areas_of_conflict.length > 0 && (
          <BlurFade delay={0.1} inView>
            <div className="border border-border/80 rounded-xl p-5 border-l-4 border-l-amber-500 bg-amber-500/[0.02] flex items-start gap-4">
              <AlertTriangle className="h-5 w-5 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
              <div className="space-y-2">
                <h3 className="font-semibold text-sm text-amber-800 dark:text-amber-400">Areas of Conflict / Disagreement</h3>
                <ul className="space-y-1.5">
                  {synthesis.areas_of_conflict.map((item, idx) => (
                    <li key={idx} className="text-sm text-muted-foreground leading-relaxed">
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </BlurFade>
        )}

        {synthesis.evidence_gaps.length > 0 && (
          <BlurFade delay={0.15} inView>
            <div className="border border-border/80 rounded-xl p-5 border-l-4 border-l-rose-500 bg-rose-500/[0.02] flex items-start gap-4">
              <HelpCircle className="h-5 w-5 text-rose-600 dark:text-rose-400 shrink-0 mt-0.5" />
              <div className="space-y-2">
                <h3 className="font-semibold text-sm text-rose-800 dark:text-rose-400">Evidence Gaps</h3>
                <ul className="space-y-1.5">
                  {synthesis.evidence_gaps.map((gap, idx) => (
                    <li key={idx} className="text-sm text-muted-foreground leading-relaxed">
                      {gap}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </BlurFade>
        )}
      </div>

      {/* Topic Clusters Section */}
      <div className="space-y-4">
        <h2 className="text-xl font-bold tracking-tight flex items-center gap-2">
          <TrendingUp className="h-5 w-5 text-muted-foreground" />
          Topic Clusters Detail
        </h2>

        <div className="grid grid-cols-1 gap-4">
          {synthesis.topics.map((topic, idx) => {
            const isExpanded = expandedTopic === topic.topic;
            return (
              <BlurFade key={topic.topic} delay={0.1 + idx * 0.05} inView>
                <div 
                  className={`border rounded-xl bg-card overflow-hidden transition-all duration-300 hover:shadow-sm ${
                    isExpanded ? 'border-primary' : 'border-border'
                  }`}
                >
                  {/* Topic Header Accordion Trigger */}
                  <div 
                    className="p-5 flex items-center justify-between cursor-pointer select-none gap-4"
                    onClick={() => setExpandedTopic(isExpanded ? null : topic.topic)}
                  >
                    <div className="space-y-1.5 flex-1">
                      <div className="flex items-center gap-2 flex-wrap">
                        <h3 className="font-bold text-lg leading-snug">{topic.topic}</h3>
                        {topic.consensus?.has_conflict && (
                          <Badge variant="outline" className="bg-amber-500/10 text-amber-600 border-amber-500/20 text-[10px] uppercase font-semibold">
                            Conflict Detected
                          </Badge>
                        )}
                      </div>
                      <div className="flex items-center gap-4 text-xs text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <Layers className="h-3.5 w-3.5" />
                          {topic.claims?.length || 0} claim{topic.claims?.length !== 1 ? 's' : ''}
                        </span>
                        <span>•</span>
                        <span>Agreement: {((topic.consensus?.agreement_ratio || 0) * 100).toFixed(0)}%</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
                      <Badge className={getConsensusBadgeStyle(topic.consensus?.evidence_strength || 'thin')}>
                        {topic.consensus?.evidence_strength || 'thin'} evidence
                      </Badge>
                      <button className="text-muted-foreground hover:text-foreground">
                        {isExpanded ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}
                      </button>
                    </div>
                  </div>

                  {/* Expanded Content Details */}
                  {isExpanded && (
                    <div className="border-t border-border bg-muted/[0.02] p-5 space-y-6">
                      {topic.consensus?.has_conflict && (
                        <div className="bg-amber-500/5 text-amber-600 dark:text-amber-400 border border-amber-500/20 rounded-lg p-3 text-sm flex items-center gap-2">
                          <AlertTriangle className="h-4 w-4" />
                          <span>This cluster contains claims with conflicting or contradicting conclusions. View relations details below.</span>
                        </div>
                      )}

                      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Claims Panel */}
                        <div className="space-y-3">
                          <h4 className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                            <FileText className="h-3.5 w-3.5" />
                            Claims List
                          </h4>
                          <div className="space-y-3 max-h-[400px] overflow-y-auto pr-1">
                            {topic.claims?.map((claim: any, cidx: number) => (
                              <div key={cidx} className="bg-card border border-border/60 rounded-lg p-3.5 space-y-2">
                                <div className="flex items-center justify-between gap-2">
                                  <Badge className={`text-[10px] capitalize ${getClaimTypeStyle(claim.claim_type)}`}>
                                    {claim.claim_type}
                                  </Badge>
                                  <span className="text-[10px] text-muted-foreground font-mono">{claim.paper_id}</span>
                                </div>
                                <p className="text-sm leading-relaxed">{claim.text}</p>
                                <div className="text-[10px] text-muted-foreground/60 flex justify-between">
                                  <span>{claim.source_section}</span>
                                  <span>Page {claim.page_number}</span>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Relations Panel */}
                        <div className="space-y-3">
                          <h4 className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                            <GitMerge className="h-3.5 w-3.5" />
                            Cross-Source Relations
                          </h4>
                          <div className="space-y-3 max-h-[400px] overflow-y-auto pr-1">
                            {topic.relations && topic.relations.length > 0 ? (
                              topic.relations.map((rel: any, ridx: number) => (
                                <div key={ridx} className="bg-card border border-border/60 rounded-lg p-3.5 space-y-2">
                                  <div className="flex items-center justify-between gap-2">
                                    <div className="flex items-center gap-1.5">
                                      <Badge className={`text-[10px] uppercase font-semibold ${getRelationTypeStyle(rel.relation_type)}`}>
                                        {rel.relation_type}
                                      </Badge>
                                      <span className="text-[10px] text-muted-foreground">
                                        {(rel.confidence * 100).toFixed(0)}% confidence
                                      </span>
                                    </div>
                                    <span className="text-[10px] text-muted-foreground font-mono">
                                      {rel.claim_ids?.join(' ↔ ')}
                                    </span>
                                  </div>
                                  <p className="text-sm text-muted-foreground leading-relaxed bg-muted/20 p-2.5 rounded border border-border/30">
                                    {rel.explanation}
                                  </p>
                                </div>
                              ))
                            ) : (
                              <div className="text-center py-8 text-xs text-muted-foreground/60 border border-dashed rounded-lg">
                                No relations detected. Make sure claims are from multiple papers.
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </BlurFade>
            );
          })}
        </div>
      </div>
    </div>
  );
}