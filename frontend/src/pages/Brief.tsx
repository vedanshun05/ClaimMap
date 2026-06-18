import { useState } from 'react';
import { getBrief, exportBrief } from '../api/client';
import type { ResearchBrief } from '../api/client';
import { Card, CardContent } from '@/components/ui/card';
import { ShinyButton } from '@/components/ui/shiny-button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { BlurFade } from '@/components/ui/blur-fade';
import { 
  Sparkles, 
  Search, 
  FileText, 
  Download, 
  FileCode, 
  Loader2, 
  BookOpen, 
  Layers, 
  CheckCircle2, 
  AlertTriangle, 
  HelpCircle, 
  ArrowRight,
  TrendingUp,
  Bookmark
} from 'lucide-react';

export default function Brief() {
  const [brief, setBrief] = useState<ResearchBrief | null>(null);
  const [query, setQuery] = useState('Transformer and BERT research');
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState('');
  const [exporting, setExporting] = useState<'md' | 'bibtex' | null>(null);
  const [exportContent, setExportContent] = useState('');

  const generateBrief = async () => {
    setGenerating(true);
    setLoading(true);
    setError('');
    try {
      const data = await getBrief(query);
      if (data.success) {
        setBrief(data.brief);
      } else {
        setError(data.message || 'Failed to generate brief');
      }
    } catch (error) {
      console.error('Failed to generate brief:', error);
      setError('Failed to generate brief. Make sure the backend is running and claims are extracted.');
    }
    setGenerating(false);
    setLoading(false);
  };

  const handleExport = async (format: 'md' | 'bibtex') => {
    setExporting(format);
    try {
      const data = await exportBrief(format, query);
      if (data.success) {
        setExportContent(data.content);
      }
    } catch (error) {
      console.error('Failed to export:', error);
    }
    setExporting(null);
  };

  const downloadFile = (content: string, filename: string) => {
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
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

  if (loading && !brief) {
    return (
      <div className="space-y-8 max-w-5xl mx-auto py-4">
        <div className="space-y-2">
          <div className="h-10 bg-muted rounded w-1/3 animate-pulse" />
          <div className="h-5 bg-muted rounded w-1/2 animate-pulse" />
        </div>

        <Card className="border border-border bg-card/50 overflow-hidden relative">
          <div className="absolute top-0 left-0 right-0 h-1 bg-muted overflow-hidden">
            <div className="h-full bg-primary animate-infinite-loading w-1/3 rounded-full" />
          </div>
          <CardContent className="p-10 flex flex-col items-center justify-center text-center space-y-4">
            <Loader2 className="h-8 w-8 text-primary animate-spin" />
            <div className="space-y-1">
              <h3 className="font-semibold text-lg">Generating Research Brief</h3>
              <p className="text-sm text-muted-foreground max-w-md">
                Synthesizing literature findings and formatting citation tags for query: <span className="font-semibold text-foreground">"{query}"</span>.
              </p>
            </div>
            <div className="w-full max-w-xs bg-muted rounded-full h-1.5 overflow-hidden mt-2">
              <div className="h-full bg-gradient-to-r from-blue-500 to-purple-500 animate-pulse" style={{ width: '70%' }} />
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error && !brief) {
    return (
      <div className="space-y-6 max-w-4xl mx-auto py-8">
        <h1 className="text-3xl font-bold tracking-tight">Research Brief</h1>
        <div className="bg-destructive/5 text-destructive border border-destructive/20 rounded-xl p-8 flex flex-col items-center gap-4 text-center">
          <AlertTriangle className="h-10 w-10 text-destructive" />
          <div className="space-y-1">
            <h3 className="font-semibold text-lg">Failed to Generate Brief</h3>
            <p className="text-sm text-muted-foreground max-w-md">{error}</p>
          </div>
          <ShinyButton onClick={generateBrief} className="mt-2">Retry Generation</ShinyButton>
        </div>
      </div>
    );
  }

  const evidenceStrength = brief?.evidence_strength_index || [];

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Title section */}
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-primary" />
          <span className="text-xs font-semibold uppercase tracking-wider text-primary/80">Structured Synthesis Output</span>
        </div>
        <h1 className="text-4xl font-extrabold tracking-tight">Research Brief</h1>
        <p className="text-sm text-muted-foreground">
          Generate a comprehensive literature brief with inline citations and evidence strength mappings.
        </p>
      </div>

      {/* Control bar */}
      <div className="flex flex-wrap gap-3 items-center bg-muted/20 p-3 rounded-2xl border border-border">
        <div className="relative flex-1 min-w-[280px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground/80" />
          <Input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter research topic..."
            className="pl-9 text-sm py-5 rounded-lg border-border"
          />
        </div>
        
        <ShinyButton onClick={generateBrief} disabled={generating} className="px-5 py-2.5 h-[42px] font-semibold text-xs">
          {generating ? (
            <>
              <Loader2 className="h-3.5 w-3.5 animate-spin mr-1.5" />
              Generating...
            </>
          ) : (
            <>
              <Sparkles className="h-3.5 w-3.5 mr-1.5" />
              Generate Brief
            </>
          )}
        </ShinyButton>

        <div className="flex gap-2">
          <ShinyButton 
            onClick={() => handleExport('md')} 
            disabled={exporting === 'md' || !brief}
            className="px-4 py-2.5 h-[42px] font-semibold text-xs border border-border"
          >
            <FileText className="h-3.5 w-3.5 mr-1.5" />
            Markdown
          </ShinyButton>
          <ShinyButton 
            onClick={() => handleExport('bibtex')} 
            disabled={exporting === 'bibtex' || !brief}
            className="px-4 py-2.5 h-[42px] font-semibold text-xs border border-border"
          >
            <FileCode className="h-3.5 w-3.5 mr-1.5" />
            BibTeX
          </ShinyButton>
        </div>
      </div>

      {/* Export Dialog overlay */}
      {exportContent && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={() => setExportContent('')}>
          <BlurFade delay={0.05} inView>
            <div className="bg-card border border-border rounded-xl p-6 max-w-3xl w-full mx-4 max-h-[85vh] overflow-hidden flex flex-col shadow-2xl" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between border-b border-border/60 pb-3 mb-4">
              <h2 className="text-lg font-bold flex items-center gap-2">
                <FileText className="h-5 w-5 text-primary" />
                Exported Research Brief
              </h2>
            </div>
            
            <pre className="text-xs bg-muted/40 border border-border/60 rounded-lg p-4 overflow-auto flex-1 font-mono whitespace-pre-wrap leading-relaxed text-muted-foreground">
              {exportContent}
            </pre>
            
            <div className="flex gap-3 mt-5 pt-3 border-t border-border/40">
              <ShinyButton 
                onClick={() => downloadFile(exportContent, `research_brief.${exporting || 'md'}`)}
                className="px-5 py-2"
              >
                <Download className="h-4 w-4 mr-1.5" />
                Download File
              </ShinyButton>
              <button
                onClick={() => setExportContent('')}
                className="px-5 py-2 text-xs font-semibold rounded-lg bg-muted hover:bg-muted/80 border border-border transition-colors ml-auto"
              >
                Close
              </button>
            </div>
          </div>
        </BlurFade>
        </div>
      )}

      {brief ? (
        <div className="space-y-8">
          {/* Brief Meta summary */}
          <div className="text-center space-y-1.5 pb-6 border-b border-border/80">
            <h2 className="text-2xl font-extrabold tracking-tight">{brief.query}</h2>
            <p className="text-sm text-muted-foreground flex items-center justify-center gap-1.5">
              <BookOpen className="h-4 w-4" />
              {brief.papers_analyzed} paper{brief.papers_analyzed !== 1 ? 's' : ''} analyzed
            </p>
          </div>

          {/* Executive Summary */}
          <BlurFade delay={0.1} inView>
            <Card className="border border-border/80 overflow-hidden bg-card">
              <CardContent className="p-6 space-y-3">
                <h3 className="text-base font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
                  <Bookmark className="h-4 w-4 text-primary" />
                  Executive Summary
                </h3>
                <p className="text-sm leading-relaxed text-foreground/90 font-medium">
                  {brief.executive_summary}
                </p>
              </CardContent>
            </Card>
          </BlurFade>

          {/* Key Themes grid */}
          {brief.themes && brief.themes.length > 0 && (
            <div className="space-y-4">
              <h3 className="text-lg font-bold tracking-tight flex items-center gap-2 text-muted-foreground">
                <Layers className="h-4 w-4" />
                Key Themes
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {brief.themes.map((theme, idx) => (
                  <BlurFade key={idx} delay={0.15 + idx * 0.04} inView>
                    <Card className="h-full border border-border/60 bg-card hover:shadow-sm transition-shadow">
                      <CardContent className="p-5 space-y-3 flex flex-col h-full">
                        <div className="flex items-start justify-between gap-3">
                          <h4 className="font-bold text-base leading-snug">{theme.theme}</h4>
                          <div className="flex gap-1.5 shrink-0">
                            {theme.evidence_count !== undefined && (
                              <Badge variant="outline" className="text-[10px] bg-muted/50 border-border">
                                {theme.evidence_count} paper{theme.evidence_count !== 1 ? 's' : ''}
                              </Badge>
                            )}
                            <Badge className={`text-[10px] capitalize ${getConsensusBadgeStyle(theme.consensus_level || 'thin')}`}>
                              {theme.consensus_level}
                            </Badge>
                          </div>
                        </div>
                        <p className="text-xs text-muted-foreground leading-relaxed flex-1">
                          {theme.summary}
                        </p>
                      </CardContent>
                    </Card>
                  </BlurFade>
                ))}
              </div>
            </div>
          )}

          {/* Evidence Strength Index */}
          {evidenceStrength.length > 0 && (
            <BlurFade delay={0.2} inView>
              <Card className="border border-border/85 bg-card">
                <CardContent className="p-6 space-y-4">
                  <h3 className="text-base font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
                    <TrendingUp className="h-4 w-4 text-primary" />
                    Evidence Strength Index
                  </h3>
                  <div className="divide-y divide-border/40">
                    {evidenceStrength.map((entry, idx) => (
                      <div key={idx} className="flex items-center gap-4 py-3 text-sm first:pt-0 last:pb-0">
                        <span className={`text-lg shrink-0 ${
                          entry.strength === 'strong' ? 'text-emerald-500' :
                          entry.strength === 'moderate' ? 'text-amber-500' :
                          'text-zinc-400'
                        }`}>
                          {entry.strength === 'strong' ? '●' : entry.strength === 'moderate' ? '◐' : '○'}
                        </span>
                        <span className="flex-1 font-medium text-foreground/90">{entry.finding}</span>
                        <Badge variant="outline" className="text-[10px] bg-muted/30 uppercase shrink-0 font-semibold tracking-wider">
                          {entry.supporting_papers} paper{entry.supporting_papers !== 1 ? 's' : ''}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </BlurFade>
          )}

          {/* Consensus Alert Panel */}
          {brief.areas_of_consensus && brief.areas_of_consensus.length > 0 && (
            <BlurFade delay={0.25} inView>
              <div className="border border-border/80 rounded-xl p-5 border-l-4 border-l-emerald-500 bg-emerald-500/[0.02] flex items-start gap-4">
                <CheckCircle2 className="h-5 w-5 text-emerald-600 dark:text-emerald-400 shrink-0 mt-0.5" />
                <div className="space-y-2">
                  <h3 className="font-semibold text-sm text-emerald-800 dark:text-emerald-400">Areas of Consensus</h3>
                  <ul className="space-y-1.5">
                    {brief.areas_of_consensus.map((item, idx) => (
                      <li key={idx} className="text-sm text-muted-foreground leading-relaxed flex items-start gap-2">
                        <span>•</span> <span dangerouslySetInnerHTML={{ __html: item }} />
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </BlurFade>
          )}

          {/* Conflict Alert Panel */}
          {brief.areas_of_conflict && brief.areas_of_conflict.length > 0 && (
            <BlurFade delay={0.3} inView>
              <div className="border border-border/80 rounded-xl p-5 border-l-4 border-l-amber-500 bg-amber-500/[0.02] flex items-start gap-4">
                <AlertTriangle className="h-5 w-5 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
                <div className="space-y-2">
                  <h3 className="font-semibold text-sm text-amber-800 dark:text-amber-400">Areas of Conflict / Disagreement</h3>
                  <ul className="space-y-1.5">
                    {brief.areas_of_conflict.map((item, idx) => (
                      <li key={idx} className="text-sm text-muted-foreground leading-relaxed flex items-start gap-2">
                        <span>•</span> <span dangerouslySetInnerHTML={{ __html: item }} />
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </BlurFade>
          )}

          {/* Research Gaps Panel */}
          {brief.open_questions && brief.open_questions.length > 0 && (
            <BlurFade delay={0.35} inView>
              <div className="border border-border/80 rounded-xl p-5 border-l-4 border-l-rose-500 bg-rose-500/[0.02] flex items-start gap-4">
                <HelpCircle className="h-5 w-5 text-rose-600 dark:text-rose-400 shrink-0 mt-0.5" />
                <div className="space-y-2">
                  <h3 className="font-semibold text-sm text-rose-800 dark:text-rose-400">Open Research Gaps</h3>
                  <ul className="space-y-1.5">
                    {brief.open_questions.map((item, idx) => (
                      <li key={idx} className="text-sm text-muted-foreground leading-relaxed flex items-start gap-2">
                        <span>•</span> {item}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </BlurFade>
          )}

          {/* Recommended next papers Panel */}
          {brief.recommended_next_papers && brief.recommended_next_papers.length > 0 && (
            <BlurFade delay={0.4} inView>
              <div className="border border-border/80 rounded-xl p-5 border-l-4 border-l-blue-500 bg-blue-500/[0.02] flex items-start gap-4">
                <ArrowRight className="h-5 w-5 text-blue-600 dark:text-blue-400 shrink-0 mt-0.5" />
                <div className="space-y-2">
                  <h3 className="font-semibold text-sm text-blue-800 dark:text-blue-400">Recommended Next Papers</h3>
                  <ul className="space-y-1.5">
                    {brief.recommended_next_papers.map((paper, idx) => (
                      <li key={idx} className="text-sm text-muted-foreground leading-relaxed flex items-start gap-2">
                        <span>•</span> {paper}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </BlurFade>
          )}
        </div>
      ) : (
        <div className="text-center py-16 border border-dashed rounded-2xl bg-muted/[0.01]">
          <FileText className="h-12 w-12 text-muted-foreground/30 mx-auto mb-3" />
          <p className="text-sm text-muted-foreground">No brief has been generated yet for this session.</p>
        </div>
      )}
    </div>
  );
}