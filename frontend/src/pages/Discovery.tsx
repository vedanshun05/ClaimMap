import { useState, useRef } from 'react';
import { searchPapers, ingestPaper, uploadPdf } from '../api/client';
import type { PaperSearchResult } from '../api/client';
import { Card, CardContent } from '@/components/ui/card';
import { ShinyButton } from '@/components/ui/shiny-button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { BlurFade } from '@/components/ui/blur-fade';
import { MagicCard } from '@/components/ui/magic-card';
import { 
  Search, 
  UploadCloud, 
  CheckSquare, 
  AlertCircle, 
  Sparkles,
  Calendar,
  User,
  CheckCircle2,
  Loader2
} from 'lucide-react';

export default function Discovery() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<PaperSearchResult[]>([]);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(false);
  const [ingesting, setIngesting] = useState(false);
  const [message, setMessage] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState('');
  const [activeTab, setActiveTab] = useState<'search' | 'upload'>('search');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setMessage('');
    try {
      const papers = await searchPapers(query, 10);
      setResults(Array.isArray(papers) ? papers : []);
      setSelected(new Set());
    } catch (error: unknown) {
      console.error('Search failed:', error);
      const msg = error instanceof Error ? error.message : String(error);
      setMessage(`Search failed: ${msg}. Make sure the backend is running.`);
      setResults([]);
    }
    setLoading(false);
  };

  const handleSelect = (paperId: string) => {
    const newSelected = new Set(selected);
    if (newSelected.has(paperId)) {
      newSelected.delete(paperId);
    } else {
      newSelected.add(paperId);
    }
    setSelected(newSelected);
  };

  const handleIngest = async () => {
    if (selected.size === 0) return;
    setIngesting(true);
    setMessage('');
    const successIds: string[] = [];
    const failIds: string[] = [];

    for (const paperId of selected) {
      try {
        await ingestPaper(paperId);
        successIds.push(paperId);
      } catch (error) {
        console.error(`Failed to ingest ${paperId}:`, error);
        failIds.push(paperId);
      }
    }

    if (failIds.length > 0) {
      setMessage(`Ingested ${successIds.length} papers. Failed: ${failIds.join(', ')}`);
    } else {
      setMessage(`Successfully ingested ${successIds.length} papers!`);
    }

    setSelected(new Set());
    setIngesting(false);
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setUploadMessage('Please select a PDF file.');
      return;
    }

    setUploading(true);
    setUploadMessage('');
    try {
      const result = await uploadPdf(file);
      setUploadMessage(`Uploaded "${result.title}" — ${result.sections_count} pages processed.`);
    } catch (error) {
      console.error('Upload failed:', error);
      setUploadMessage('Upload failed. Make sure the backend is running.');
    }
    setUploading(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Title section */}
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-primary" />
          <span className="text-xs font-semibold uppercase tracking-wider text-primary/80">Discover & Add Literature</span>
        </div>
        <h1 className="text-4xl font-extrabold tracking-tight">Paper Discovery</h1>
        <p className="text-sm text-muted-foreground">
          Query arXiv to fetch academic literature, or upload your own PDFs to extract core claims.
        </p>
      </div>

      {/* Segmented Controls (Tab Buttons) */}
      <div className="flex bg-muted/60 p-1 rounded-xl max-w-[320px] border border-border">
        <button
          onClick={() => setActiveTab('search')}
          className={`flex-1 flex items-center justify-center gap-2 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
            activeTab === 'search'
              ? 'bg-background text-foreground shadow-sm border border-border/40'
              : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          <Search className="h-4 w-4" />
          Search arXiv
        </button>
        <button
          onClick={() => setActiveTab('upload')}
          className={`flex-1 flex items-center justify-center gap-2 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
            activeTab === 'upload'
              ? 'bg-background text-foreground shadow-sm border border-border/40'
              : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          <UploadCloud className="h-4 w-4" />
          Upload PDF
        </button>
      </div>

      {activeTab === 'search' && (
        <div className="space-y-6">
          {/* Search bar */}
          <div className="flex gap-3 items-center">
            <div className="relative flex-1">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground/80" />
              <Input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Enter topic or paper name (e.g. 'retrieval augmented generation')"
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                className="pl-11 text-base py-6 rounded-xl border-border"
              />
            </div>
            <ShinyButton
              onClick={handleSearch}
              disabled={loading}
              className="px-8 py-3.5 h-[50px] font-semibold"
            >
              {loading ? 'Searching...' : 'Search'}
            </ShinyButton>
          </div>

          {/* Ingest Alert bar */}
          {selected.size > 0 && (
            <BlurFade delay={0.05} inView>
              <div className="flex items-center justify-between bg-primary/[0.03] border border-primary/20 rounded-xl p-4 shadow-sm">
                <span className="text-sm font-medium flex items-center gap-2">
                  <CheckSquare className="h-4 w-4 text-primary" />
                  {selected.size} paper{selected.size !== 1 ? 's' : ''} selected for ingestion
                </span>
                <ShinyButton onClick={handleIngest} disabled={ingesting} className="px-6 py-2.5">
                  {ingesting ? 'Ingesting...' : 'Ingest Selected'}
                </ShinyButton>
              </div>
            </BlurFade>
          )}

          {message && (
            <div className="bg-primary/[0.03] text-primary border border-primary/25 rounded-xl p-4 text-sm flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4 shrink-0" />
              <span>{message}</span>
            </div>
          )}

          {/* Search Results Grid */}
          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="border border-border/80 rounded-xl p-5 space-y-4 animate-pulse bg-card/30">
                  <div className="h-5 bg-muted rounded w-3/4" />
                  <div className="flex gap-2">
                    <div className="h-4 bg-muted rounded w-16" />
                    <div className="h-4 bg-muted rounded w-12" />
                  </div>
                  <div className="space-y-2 pt-2">
                    <div className="h-3 bg-muted rounded w-full" />
                    <div className="h-3 bg-muted rounded w-5/6" />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {results.map((paper, idx) => (
                <BlurFade key={paper.paper_id} delay={idx * 0.03} inView>
                  <MagicCard
                    mode="gradient"
                    gradientColor="var(--muted)"
                    className={`cursor-pointer border transition-all duration-300 rounded-xl overflow-hidden ${
                      selected.has(paper.paper_id) 
                        ? 'border-primary ring-1 ring-primary' 
                        : 'border-border hover:border-border/80'
                    }`}
                    onClick={() => handleSelect(paper.paper_id)}
                  >
                    <div className="p-5 space-y-3">
                      <div className="flex items-start gap-3">
                        <input
                          type="checkbox"
                          checked={selected.has(paper.paper_id)}
                          onChange={() => handleSelect(paper.paper_id)}
                          onClick={(e) => e.stopPropagation()}
                          className="mt-1 h-4 w-4 rounded border-border text-primary focus:ring-primary cursor-pointer"
                        />
                        <h3 className="font-semibold text-sm leading-snug flex-1">{paper.title}</h3>
                      </div>

                      <div className="flex items-center gap-4 text-xs text-muted-foreground flex-wrap">
                        <Badge className="bg-primary/10 text-primary border border-primary/20 text-[10px] capitalize">
                          {paper.source}
                        </Badge>
                        <span className="flex items-center gap-1">
                          <Calendar className="h-3.5 w-3.5" />
                          {paper.year || 'N/A'}
                        </span>
                        <span className="ml-auto font-medium bg-muted px-2 py-0.5 rounded text-[10px]">
                          Relevance: {paper.relevance_score.toFixed(2)}
                        </span>
                      </div>

                      <p className="text-xs text-muted-foreground line-clamp-3 leading-relaxed">
                        {paper.abstract || 'No abstract description available.'}
                      </p>

                      <div className="text-[10px] text-muted-foreground/80 flex items-center gap-1 border-t border-border/40 pt-2.5">
                        <User className="h-3.5 w-3.5 shrink-0" />
                        <span className="truncate">
                          {(paper.authors ?? []).slice(0, 3).join(', ')}
                          {(paper.authors ?? []).length > 3 && ' et al.'}
                        </span>
                      </div>
                    </div>
                  </MagicCard>
                </BlurFade>
              ))}
            </div>
          )}

          {results.length === 0 && !loading && (
            <div className="text-center py-16 border border-dashed rounded-2xl bg-muted/[0.01]">
              <Search className="h-12 w-12 text-muted-foreground/30 mx-auto mb-3" />
              <p className="text-sm text-muted-foreground">Enter a search query above to browse papers from arXiv.</p>
            </div>
          )}
        </div>
      )}

      {activeTab === 'upload' && (
        <BlurFade delay={0.05} inView>
          <Card className="border border-border bg-card/50 overflow-hidden rounded-2xl relative">
            <CardContent className="p-10 space-y-6 text-center max-w-2xl mx-auto flex flex-col items-center">
              <div className="p-4 bg-primary/5 rounded-full border border-primary/10">
                <UploadCloud className="h-8 w-8 text-primary" />
              </div>
              <div className="space-y-1.5">
                <h3 className="text-xl font-bold tracking-tight">Upload Local PDF</h3>
                <p className="text-sm text-muted-foreground max-w-md mx-auto">
                  Drag and drop or select a local PDF research paper. The engine will parse sections and pages to extract claims.
                </p>
              </div>

              <div className="w-full relative border border-dashed border-border rounded-xl p-8 hover:bg-muted/10 transition-colors duration-200">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf"
                  onChange={handleUpload}
                  className="absolute inset-0 opacity-0 cursor-pointer"
                  disabled={uploading}
                />
                <div className="text-sm font-semibold text-primary">
                  Click or drag file here
                </div>
                <div className="text-xs text-muted-foreground mt-1">
                  PDF format only (Max 20MB)
                </div>
              </div>

              {uploading && (
                <div className="flex items-center gap-2 text-sm text-primary animate-pulse">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Parsing sections and indexing paper content...
                </div>
              )}

              {uploadMessage && (
                <div className={`text-sm rounded-xl p-3.5 border w-full flex items-start gap-2.5 text-left ${
                  uploadMessage.includes('failed') || uploadMessage.includes('Failed')
                    ? 'bg-rose-500/5 text-rose-600 dark:text-rose-400 border-rose-500/20'
                    : 'bg-emerald-500/5 text-emerald-600 dark:text-emerald-400 border-emerald-500/20'
                }`}>
                  {uploadMessage.includes('failed') || uploadMessage.includes('Failed') ? (
                    <AlertCircle className="h-5 w-5 shrink-0 text-rose-500" />
                  ) : (
                    <CheckCircle2 className="h-5 w-5 shrink-0 text-emerald-500" />
                  )}
                  <span>{uploadMessage}</span>
                </div>
              )}
            </CardContent>
          </Card>
        </BlurFade>
      )}
    </div>
  );
}