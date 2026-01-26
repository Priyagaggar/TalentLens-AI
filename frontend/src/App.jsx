import { ScanEye, Github, FileText, BarChart3, History } from 'lucide-react';
import ResumeUploader from './components/ResumeUploader';

function App() {
  return (
    <div className="min-h-screen flex flex-col font-sans text-slate-900 selection:bg-primary-100 selection:text-primary-900 overflow-x-hidden">

      {/* Dynamic Background */}
      <div className="fixed inset-0 -z-50 h-full w-full bg-slate-50">
        <div className="absolute top-0 z-[-2] h-screen w-screen bg-[radial-gradient(100%_50%_at_50%_0%,rgba(0,163,255,0.13)_0,rgba(0,163,255,0)_50%,rgba(0,163,255,0)_100%)]"></div>
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]"></div>
      </div>

      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b border-white/20 bg-white/70 backdrop-blur-md supports-[backdrop-filter]:bg-white/50 shadow-sm">
        <div className="container mx-auto px-4 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="relative group">
              <div className="absolute -inset-1 rounded-lg bg-gradient-to-r from-primary-600 to-indigo-600 opacity-75 blur transition duration-200 group-hover:opacity-100" />
              <div className="relative w-9 h-9 rounded-lg bg-white flex items-center justify-center text-primary-600 shadow-sm">
                <ScanEye className="w-5 h-5 fill-primary-100" />
              </div>
            </div>
            <span className="font-display font-bold text-xl tracking-tight text-slate-800">TalentLens <span className="text-primary-600">AI</span></span>
          </div>

          <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-600">
            <a href="#" className="flex items-center gap-2 hover:text-primary-600 transition-colors">
              <FileText className="w-4 h-4" /> Dashboard
            </a>
            <a href="#" className="flex items-center gap-2 hover:text-primary-600 transition-colors">
              <History className="w-4 h-4" /> History
            </a>
          </nav>

          <div className="flex items-center gap-4">
            <a href="https://github.com" target="_blank" rel="noreferrer" className="text-slate-400 hover:text-slate-900 transition-colors p-2 hover:bg-slate-100/50 rounded-full">
              <Github className="w-5 h-5" />
            </a>
            <button className="hidden sm:flex px-4 py-2 rounded-full bg-slate-900 text-white text-xs font-semibold hover:bg-slate-800 transition-all shadow-lg shadow-slate-900/20">
              Get Started
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 py-12 px-4 sm:px-6">
        <ResumeUploader />
      </main>

      {/* Footer */}
      <footer className="py-8 border-t border-slate-200/60 bg-white/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 text-center">
          <p className="flex items-center justify-center gap-2 text-sm text-slate-500 font-medium">
            © {new Date().getFullYear()} TalentLens AI. Built for <span className="text-indigo-600 font-bold">Precision Hiring</span>.
          </p>
        </div>
      </footer>

    </div>
  );
}

export default App;
