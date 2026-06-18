import { useState, useEffect, useCallback } from 'react';
import { listPapers, extractClaims } from '../api/client';
import type { Paper, Claim } from '../api/client';
import { ShinyButton } from '@/components/ui/shiny-button';
import { Badge } from '@/components/ui/badge';
import { BlurFade } from '@/components/ui/blur-fade';
import { 
  Sparkles, 
  Calendar, 
  Layers, 
  ChevronDown, 
  ChevronUp, 
  User, 
  BookOpen, 
  Wand2, 
  Loader2, 
  CheckCircle2,
  Bookmark
} from 'lucide-react';

interface ProgressState {
  isExtracting: boolean;
  currentSection: string;
  current: number;
  total: number;
  claimsSoFar: number;
}

export default function Papers() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [paperClaims, setPaperClaims] = useState<Record<string, Claim[]>>({});
  const [extractingId, setExtractingId] = useState<string | null>(null);
  const [progress, setProgress] = useState<Record<string, ProgressState>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPapers();
  }, []);

  const loadPapers = async () => {
    setLoading(true);
    try {
      const data = await listPapers();
      setPapers(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Failed to load papers:', error);
      setPapers([]);
    }
    setLoading(false);
  };

  const handleExpand = (paperId: string) => {
    setExpandedId(expandedId === paperId ? null : paperId);
  };

  const handleExtract = useCallback(async (paperId: string) => {
    setExtractingId(paperId);
    setProgress(prev => ({
      ...prev,
      [paperId]: { isExtracting: true, currentSection: 'Starting...', current: 0, total: 0, claimsSoFar: 0 }
    }));

    try {
      const evtSource = new EventSource(`http://localhost:8000/api/papers/${encodeURIComponent(paperId)}/extract/stream`);
      let useEventSource = true;

      evtSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'start') {
            setProgress(prev => ({
              ...prev,
              [paperId]: { isExtracting: true, currentSection: 'Analyzing...', current: 0, total: data.total_sections, claimsSoFar: 0 }
            }));
          } else if (data.type === 'progress') {
            setProgress(prev => ({
              ...prev,
              [paperId]: {
                ...prev[paperId],
                currentSection: data.section,
                current: data.current,
                total: data.total,
              }
            }));
          } else if (data.type === 'section_done') {
            setProgress(prev => ({
              ...prev,
              [paperId]: {
                ...prev[paperId],
                claimsSoFar: data.total_claims_so_far,
              }
            }));
          } else if (data.type === 'complete') {
            setPaperClaims(prev => ({ ...prev, [paperId]: (data.claims ?? []) }));
            setProgress(prev => ({
              ...prev,
              [paperId]: { isExtracting: false, currentSection: '', current: 0, total: 0, claimsSoFar: 0 }
            }));
            setExtractingId(null);
            evtSource.close();
            useEventSource = false;
          }
        } catch {
          // ignore parse errors
        }
      };

      evtSource.onerror = async () => {
        evtSource.close();
        if (!useEventSource) return;
        useEventSource = false;

        setProgress(prev => ({
          ...prev,
          [paperId]: { ...prev[paperId], currentSection: 'Extracting (fallback)...' }
        }));

        try {
          const result = await extractClaims(paperId);
          setPaperClaims(prev => ({ ...prev, [paperId]: (result.claims ?? []) }));
        } catch {
          // already handled below
        } finally {
          setExtractingId(null);
          setProgress(prev => ({
            ...prev,
            [paperId]: { isExtracting: false, currentSection: '', current: 0, total: 0, claimsSoFar: 0 }
          }));
        }
      };

      setTimeout(() => {
        if (useEventSource) {
          evtSource.close();
          useEventSource = false;
        }
      }, 300000);

    } catch {
      try {
        const result = await extractClaims(paperId);
        setPaperClaims(prev => ({ ...prev, [paperId]: (result.claims ?? []) }));
      } catch {
        // failed
      } finally {
        setExtractingId(null);
        setProgress(prev => ({
          ...prev,
          [paperId]: { isExtracting: false, currentSection: '', current: 0, total: 0, claimsSoFar: 0 }
        }));
      }
    }
  }, []);

  const progressPct = (id: string) => {
    const p = progress[id];
    if (!p || p.total === 0) return 0;
    return Math.round((p.current / p.total) * 100);
  };

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
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="border border-border/80 rounded-xl p-5 space-y-4 bg-card/30 h-24" />
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
          <span className="text-xs font-semibold uppercase tracking-wider text-primary/80">Indexed Knowledge Base</span>
        </div>
        <h1 className="text-4xl font-extrabold tracking-tight">Ingested Papers</h1>
        <p className="text-sm text-muted-foreground">
          View ingested paper sections, extract raw semantic claims, and prepare them for cross-source synthesis.
        </p>
      </div>

      {papers.length === 0 ? (
        <div className="text-center py-16 border border-dashed rounded-2xl bg-muted/[0.01]">
          <BookOpen className="h-12 w-12 text-muted-foreground/30 mx-auto mb-3" />
          <p className="text-sm text-muted-foreground">No papers ingested yet.</p>
          <div className="mt-4">
            <ShinyButton onClick={() => window.location.pathname = '/'}>
              Go to Discovery
            </ShinyButton>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {papers.map((paper, idx) => {
            const isExpanded = expandedId === paper.id;
            return (
              <BlurFade key={paper.id} delay={idx * 0.05} inView>
                <div 
                  className={`border rounded-xl bg-card transition-all duration-300 ${
                    isExpanded ? 'border-primary' : 'border-border'
                  }`}
                >
                  {/* Paper Header accordion trigger */}
                  <div
                    className="p-5 flex items-start justify-between gap-4 cursor-pointer select-none"
                    onClick={() => handleExpand(paper.id)}
                  >
                    <div className="space-y-2 flex-1">
                      <h3 className="font-bold text-lg leading-snug">{paper.title}</h3>
                      <div className="flex items-center gap-4 text-xs text-muted-foreground flex-wrap">
                        <Badge className="bg-primary/10 text-primary border border-primary/20 text-[10px] capitalize">
                          {paper.source}
                        </Badge>
                        <span className="flex items-center gap-1">
                          <Calendar className="h-3.5 w-3.5" />
                          {paper.year || 'N/A'}
                        </span>
                        <span className="flex items-center gap-1">
                          <Layers className="h-3.5 w-3.5" />
                          {(paper.sections ?? []).length} section{(paper.sections ?? []).length !== 1 ? 's' : ''}
                        </span>
                      </div>
                    </div>
                    <div className="text-muted-foreground hover:text-foreground mt-1">
                      {isExpanded ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}
                    </div>
                  </div>

                  {/* Expanded Content detail */}
                  {isExpanded && (
                    <div className="border-t border-border p-5 space-y-6 bg-muted/[0.01]">
                      {/* Authors */}
                      <div className="text-sm flex items-center gap-2 text-muted-foreground bg-muted/30 p-2.5 rounded-lg border border-border/40">
                        <User className="h-4 w-4 shrink-0 text-muted-foreground" />
                        <span className="font-medium text-foreground">
                          {(paper.authors ?? []).join(', ')}
                        </span>
                      </div>

                      {/* Abstract */}
                      <div className="space-y-2">
                        <h4 className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                          <Bookmark className="h-3.5 w-3.5" />
                          Abstract
                        </h4>
                        <p className="text-sm leading-relaxed text-muted-foreground bg-card p-4 rounded-lg border border-border/50">
                          {paper.abstract}
                        </p>
                      </div>

                      {/* Sections List */}
                      {(paper.sections ?? []).length > 0 && (
                        <div className="space-y-2">
                          <h4 className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                            <Layers className="h-3.5 w-3.5" />
                            Parsed Sections Preview (First 5)
                          </h4>
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                            {(paper.sections ?? []).slice(0, 5).map((section, sidx) => (
                              <div key={sidx} className="bg-card border border-border/50 rounded-lg p-3 space-y-1.5 hover:border-border transition-colors">
                                <div className="flex items-center justify-between text-xs text-muted-foreground border-b border-border/30 pb-1">
                                  <span className="font-semibold text-foreground truncate max-w-[180px]">{section.heading}</span>
                                  <span>Page {section.page_number}</span>
                                </div>
                                <p className="text-xs text-muted-foreground line-clamp-2 leading-relaxed">
                                  {section.content}
                                </p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Claim Extraction Controls */}
                      <div className="space-y-4 border-t border-border/60 pt-4 flex flex-col gap-3">
                        <div className="flex items-center gap-3 flex-wrap">
                          <ShinyButton
                            onClick={(e: React.MouseEvent) => {
                              e.stopPropagation();
                              handleExtract(paper.id);
                            }}
                            disabled={extractingId === paper.id}
                            className="px-6 py-2.5 font-semibold flex items-center gap-2"
                          >
                            {extractingId === paper.id ? (
                              <>
                                <Loader2 className="h-4 w-4 animate-spin" />
                                Extracting...
                              </>
                            ) : (
                              <>
                                <Wand2 className="h-4 w-4" />
                                Extract Claims
                              </>
                            )}
                          </ShinyButton>
                          
                          {progress[paper.id]?.isExtracting && (
                            <div className="flex items-center gap-2 text-xs text-primary animate-pulse">
                              <Loader2 className="h-3.5 w-3.5 animate-spin" />
                              <span>Processing section: {progress[paper.id].currentSection}</span>
                            </div>
                          )}
                        </div>

                        {/* Extraction Progress Bar */}
                        {progress[paper.id]?.isExtracting && (
                          <div className="space-y-2 bg-muted/40 p-4 rounded-xl border border-border/40">
                            <div className="flex items-center justify-between text-xs">
                              <span className="text-muted-foreground">
                                Progress: {progress[paper.id].current} / {progress[paper.id].total} sections
                              </span>
                              {progress[paper.id].claimsSoFar > 0 && (
                                <Badge className="bg-emerald-500/10 text-emerald-600 border border-emerald-500/20 text-[10px]">
                                  {progress[paper.id].claimsSoFar} claims found
                                </Badge>
                              )}
                            </div>
                            <div className="w-full bg-muted rounded-full h-2 overflow-hidden">
                              <div
                                className="h-2 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-500 ease-out"
                                style={{ width: `${progressPct(paper.id)}%` }}
                              />
                            </div>
                          </div>
                        )}

                        {/* Claims preview list */}
                        {paperClaims[paper.id] && paperClaims[paper.id].length > 0 && (
                          <div className="space-y-3 bg-muted/20 p-4 rounded-xl border border-border/40">
                            <h4 className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                              <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                              Extracted Claims ({paperClaims[paper.id].length})
                            </h4>
                            <div className="flex flex-wrap gap-2">
                              {paperClaims[paper.id].slice(0, 8).map((claim, cidx) => (
                                <span
                                  key={cidx}
                                  className={`inline-flex items-center text-xs px-2.5 py-1 rounded-full ${getClaimBadgeStyle(claim.claim_type)}`}
                                >
                                  <span className="font-semibold uppercase text-[9px] mr-1.5">{claim.claim_type}</span>
                                  <span className="truncate max-w-[200px]">{claim.text}</span>
                                </span>
                              ))}
                              {paperClaims[paper.id].length > 8 && (
                                <span className="inline-flex items-center text-xs px-2.5 py-1 rounded-full bg-muted text-muted-foreground border border-border">
                                  + {paperClaims[paper.id].length - 8} more
                                </span>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </BlurFade>
            );
          })}
        </div>
      )}
    </div>
  );
}