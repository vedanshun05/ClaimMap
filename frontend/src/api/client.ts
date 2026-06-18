import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface PaperSearchResult {
  paper_id: string;
  title: string;
  authors: string[];
  year: number;
  abstract: string;
  url: string;
  source: string;
  relevance_score: number;
  citation_count: number;
}

export interface Paper {
  id: string;
  title: string;
  authors: string[];
  year: number;
  abstract: string;
  source: string;
  source_id: string;
  pdf_path: string | null;
  sections: Section[];
  created_at: string;
}

export interface Section {
  id?: number;
  paper_id: string;
  heading: string;
  content: string;
  page_number: number;
}

export interface Claim {
  id: number;
  paper_id: string;
  text: string;
  claim_type: 'finding' | 'hypothesis' | 'limitation';
  source_section: string;
  source_sentence: string;
  page_number: number;
  confidence: number;
  is_validated: boolean;
}

export interface TopicGroup {
  topic: string;
  claims: Claim[];
  relations: Relation[];
  consensus: ConsensusScore;
}

export interface Relation {
  id?: number;
  claim_ids: string[];
  relation_type: 'agrees' | 'contradicts' | 'supports' | 'gap';
  explanation: string;
  confidence: number;
}

export interface ConsensusScore {
  topic: string;
  total_claims: number;
  agreement_ratio: number;
  has_conflict: boolean;
  evidence_strength: 'strong' | 'moderate' | 'thin';
}

export interface SynthesisResult {
  topics: TopicGroup[];
  areas_of_consensus: string[];
  areas_of_conflict: string[];
  evidence_gaps: string[];
  total_papers: number;
  total_claims: number;
}

export interface ResearchBrief {
  query: string;
  papers_analyzed: number;
  executive_summary: string;
  themes: ThemeSummary[];
  areas_of_consensus: string[];
  areas_of_conflict: string[];
  evidence_strength_index?: EvidenceStrength[];
  open_questions: string[];
  recommended_next_papers: string[];
}

export interface ThemeSummary {
  theme: string;
  summary: string;
  supporting_claim_ids: string[];
  consensus_level: 'strong' | 'moderate' | 'thin';
  evidence_count?: number;
}

export interface EvidenceStrength {
  finding: string;
  strength: 'strong' | 'moderate' | 'thin';
  supporting_papers: number;
}

export const searchPapers = async (query: string, maxResults: number = 10): Promise<PaperSearchResult[]> => {
  const response = await api.post('/search', { query, max_results: maxResults });
  return response.data.papers ?? [];
};

export const ingestPaper = async (paperId: string): Promise<{ success: boolean; paper_id: string; title: string; sections_count: number }> => {
  const response = await api.post(`/ingest/${encodeURIComponent(paperId)}`);
  return response.data;
};

export const uploadPdf = async (file: File): Promise<{ success: boolean; paper_id: string; title: string; sections_count: number; filename: string }> => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const listPapers = async (): Promise<Paper[]> => {
  const response = await api.get('/papers');
  return response.data ?? [];
};

export const getPaper = async (paperId: string): Promise<Paper> => {
  const response = await api.get(`/papers/${paperId}`);
  return response.data;
};

export const getClaims = async (paperId: string): Promise<Claim[]> => {
  const response = await api.get(`/papers/${paperId}/claims`);
  return response.data ?? [];
};

export const extractClaims = async (paperId: string): Promise<{ paper_id: string; claims: Claim[]; extraction_success: boolean; message: string }> => {
  const response = await api.post(`/papers/${paperId}/extract`);
  return response.data;
};

export const getAllClaims = async (): Promise<Claim[]> => {
  const response = await api.get('/claims/all');
  return response.data ?? [];
};

export const getSynthesis = async (): Promise<{ synthesis: SynthesisResult; success: boolean; message: string }> => {
  const response = await api.get('/synthesis');
  return response.data;
};

export const getBrief = async (query: string = 'Research on deep learning'): Promise<{ brief: ResearchBrief; success: boolean; message: string }> => {
  const response = await api.get('/brief', { params: { query } });
  return response.data;
};

export const exportBrief = async (format: 'md' | 'bibtex' | 'json', query: string = 'Research on deep learning'): Promise<{ content: string; format: string; success: boolean; message: string }> => {
  const response = await api.post('/brief/export', { format }, { params: { query } });
  return response.data;
};

export default api;