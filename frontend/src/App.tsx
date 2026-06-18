import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import { Component, useState, useEffect, type ReactNode } from 'react';
import { Sun, Moon, Network } from 'lucide-react';
import Discovery from './pages/Discovery';
import Papers from './pages/Papers';
import Claims from './pages/Claims';
import Synthesis from './pages/Synthesis';
import Brief from './pages/Brief';
import './App.css';

interface ErrorBoundaryProps {
  children: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center min-h-[50vh] gap-4 p-8">
          <h2 className="text-xl font-bold text-destructive">Something went wrong</h2>
          <p className="text-sm text-muted-foreground max-w-md">{this.state.error?.message}</p>
          <button
            onClick={() => this.setState({ hasError: false, error: null })}
            className="px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm"
          >
            Try Again
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

function App() {
  // Initialize theme from local storage or system preference
  const [theme, setTheme] = useState<'light' | 'dark'>(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('theme');
      if (saved === 'light' || saved === 'dark') return saved;
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    return 'dark';
  });

  useEffect(() => {
    const root = window.document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
    localStorage.setItem('theme', theme);
  }, [theme]);

  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
      isActive
        ? 'bg-primary text-primary-foreground font-semibold'
        : 'text-muted-foreground hover:text-foreground hover:bg-muted'
    }`;

  return (
    <BrowserRouter>
      <div className="min-h-screen flex flex-col bg-background text-foreground transition-colors duration-300">
        <nav className="sticky top-0 z-50 bg-background/80 backdrop-blur-md border-b border-border/80">
          <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
            <h1 className="text-xl font-bold tracking-tight bg-gradient-to-r from-violet-600 via-indigo-500 to-cyan-500 dark:from-violet-400 dark:via-indigo-400 dark:to-cyan-400 bg-clip-text text-transparent flex items-center gap-2">
              <Network className="h-5 w-5 text-indigo-500 dark:text-indigo-400" />
              <span className="font-extrabold">ClaimMap</span>
            </h1>
            <div className="flex items-center gap-1">
              <NavLink to="/" className={linkClass}>Discovery</NavLink>
              <NavLink to="/papers" className={linkClass}>Papers</NavLink>
              <NavLink to="/claims" className={linkClass}>Claims</NavLink>
              <NavLink to="/synthesis" className={linkClass}>Synthesis</NavLink>
              <NavLink to="/brief" className={linkClass}>Brief</NavLink>
              
              <button
                onClick={() => setTheme(prev => prev === 'light' ? 'dark' : 'light')}
                className="p-2 ml-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted transition-colors cursor-pointer"
                aria-label="Toggle Theme"
              >
                {theme === 'light' ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
              </button>
            </div>
          </div>
        </nav>

        <main className="flex-1 max-w-6xl mx-auto px-4 py-8 w-full">
          <ErrorBoundary>
            <Routes>
              <Route path="/" element={<Discovery />} />
              <Route path="/papers" element={<Papers />} />
              <Route path="/claims" element={<Claims />} />
              <Route path="/synthesis" element={<Synthesis />} />
              <Route path="/brief" element={<Brief />} />
            </Routes>
          </ErrorBoundary>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
