import React, { useState, useRef } from 'react';
import axios from 'axios';
import { Upload, FileText, Trash2, CheckCircle, AlertCircle, Loader2, Sparkles, X } from 'lucide-react';
import ResultsDashboard from './ResultsDashboard';
import { cn, formatBytes } from '../utils';

const API_BASE_URL = "http://localhost:8000/api/v1";

const ResumeUploader = () => {
    const [resumes, setResumes] = useState([]);
    const [jdText, setJdText] = useState("");
    const [isUploading, setIsUploading] = useState(false);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [results, setResults] = useState(null);
    const [error, setError] = useState(null);

    const fileInputRef = useRef(null);

    const handleFileChange = (e) => {
        if (e.target.files) {
            const newFiles = Array.from(e.target.files).filter(file =>
                ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'].includes(file.type)
            );
            // Limit to 10 files max for now to prevent overload
            if (resumes.length + newFiles.length > 10) {
                setError("You can only upload up to 10 resumes at a time.");
                return;
            }
            setResumes(prev => [...prev, ...newFiles]);
            setError(null);
        }
    };

    const removeFile = (index) => {
        setResumes(prev => prev.filter((_, i) => i !== index));
    };

    const handleAnalyze = async () => {
        if (resumes.length === 0) {
            setError("Please upload at least one resume.");
            return;
        }
        if (!jdText.trim()) {
            setError("Please enter a Job Description.");
            return;
        }

        setIsUploading(true);
        setError(null);
        setResults(null);

        try {
            // 1. Upload Resumes & JD (as text)
            const formData = new FormData();
            resumes.forEach(file => {
                formData.append('resumes', file);
            });
            formData.append('job_description_text', jdText);

            const uploadRes = await axios.post(`${API_BASE_URL}/upload/resumes`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            const { job_description_id, resume_ids } = uploadRes.data;
            setIsUploading(false);
            setIsAnalyzing(true);

            // 2. Trigger Batch Analysis
            const analysisRes = await axios.post(`${API_BASE_URL}/analyze/batch`, {
                job_description_id,
                resume_ids
            });

            setResults(analysisRes.data);

        } catch (err) {
            console.error(err);
            setError(err.response?.data?.detail || "An error occurred during processing. Please try again.");
        } finally {
            setIsUploading(false);
            setIsAnalyzing(false);
        }
    };

    return (
        <div className="max-w-6xl mx-auto space-y-12 animate-fade-in relative z-10">
            {/* Hero Section */}
            <div className="text-center space-y-6 max-w-3xl mx-auto pt-8">
                <div className="inline-flex items-center justify-center px-4 py-1.5 rounded-full bg-blue-50/50 backdrop-blur-md text-primary-700 text-sm font-semibold mb-4 border border-blue-100 shadow-sm animate-fade-in">
                    <Sparkles className="w-4 h-4 mr-2 text-primary-500" />
                    <span className="bg-gradient-to-r from-primary-700 to-indigo-700 bg-clip-text text-transparent">AI-Powered Recruiting Assistant</span>
                </div>
                <h1 className="text-4xl md:text-6xl font-display font-bold tracking-tight text-slate-900 leading-[1.1]">
                    Screen candidates <br className="hidden md:block" /> with <span className="bg-gradient-to-r from-primary-600 to-indigo-600 bg-clip-text text-transparent">superhuman speed</span>.
                </h1>
                <p className="text-lg md:text-xl text-slate-600 leading-relaxed max-w-2xl mx-auto">
                    Upload resumes and a job description. Let our AI rank candidates, extract skills, and provide intelligent match scores in seconds.
                </p>
            </div>

            <div className="grid gap-8 lg:grid-cols-2 items-start">

                {/* Left Column: Inputs */}
                <div className="space-y-6">

                    {/* Job Description Card */}
                    <div className="group bg-white/70 backdrop-blur-xl rounded-3xl p-1 shadow-xl shadow-slate-200/50 border border-white/50 transition-all hover:shadow-2xl hover:shadow-primary-900/5">
                        <div className="bg-white/50 rounded-[22px] p-6 space-y-4 h-full border border-slate-100/50">
                            <div className="flex items-center justify-between">
                                <h2 className="text-lg font-display font-bold flex items-center gap-2 text-slate-800">
                                    <div className="p-2 rounded-lg bg-indigo-50 text-indigo-600">
                                        <FileText className="w-5 h-5" />
                                    </div>
                                    Job Description
                                </h2>
                                <span className="text-[10px] font-bold px-2 py-1 rounded bg-slate-100 text-slate-500 uppercase tracking-wider border border-slate-200">Required</span>
                            </div>
                            <textarea
                                className="w-full h-72 p-4 rounded-xl border border-slate-200 bg-slate-50/50 focus:bg-white focus:ring-4 focus:ring-primary-500/10 focus:border-primary-500 transition-all resize-none text-sm leading-relaxed placeholder:text-slate-400 font-medium text-slate-700 custom-scrollbar"
                                placeholder="Paste the full job requirements, responsibilities, and qualifications here..."
                                value={jdText}
                                onChange={(e) => setJdText(e.target.value)}
                            />
                        </div>
                    </div>

                    {/* Resume Upload Card */}
                    <div className="group bg-white/70 backdrop-blur-xl rounded-3xl p-1 shadow-xl shadow-slate-200/50 border border-white/50 transition-all hover:shadow-2xl hover:shadow-primary-900/5">
                        <div className="bg-white/50 rounded-[22px] p-6 space-y-4 border border-slate-100/50">
                            <h2 className="text-lg font-display font-bold flex items-center gap-2 text-slate-800">
                                <div className="p-2 rounded-lg bg-blue-50 text-blue-600">
                                    <Upload className="w-5 h-5" />
                                </div>
                                Upload Resumes
                            </h2>

                            <div
                                className={cn(
                                    "relative border-2 border-dashed rounded-2xl p-10 text-center transition-all cursor-pointer overflow-hidden isolate",
                                    resumes.length > 0 ? "border-primary-300 bg-primary-50/30" : "border-slate-300 hover:border-primary-400 hover:bg-slate-50",
                                )}
                                onClick={() => fileInputRef.current?.click()}
                            >
                                <input
                                    type="file"
                                    multiple
                                    className="hidden"
                                    ref={fileInputRef}
                                    accept=".pdf,.docx"
                                    onChange={handleFileChange}
                                />
                                <div className="absolute inset-0 bg-gradient-to-tr from-primary-50/0 via-primary-50/0 to-primary-100/30 opacity-0 group-hover:opacity-100 transition-opacity -z-10" />

                                <div className="relative z-10 flex flex-col items-center justify-center">
                                    <div className="w-16 h-16 bg-white shadow-lg shadow-slate-200/50 rounded-2xl flex items-center justify-center mb-4 group-hover:scale-110 group-hover:-rotate-3 transition-transform duration-300">
                                        <Upload className="w-8 h-8 text-primary-600" />
                                    </div>
                                    <p className="text-base font-bold text-slate-900">
                                        Drop resumes here or <span className="text-primary-600 hover:underline">browse</span>
                                    </p>
                                    <p className="text-xs text-slate-500 mt-2 font-medium">PD & DOCX up to 5MB</p>
                                </div>
                            </div>
                        </div>
                    </div>

                </div>

                {/* Right Column: List & Actions */}
                <div className="space-y-6">

                    {/* Selected Files Panel */}
                    <div className="bg-white/80 backdrop-blur-xl rounded-3xl border border-white/60 p-6 min-h-[400px] flex flex-col shadow-xl shadow-slate-200/40">
                        <div className="flex items-center justify-between mb-6">
                            <h3 className="font-display font-bold text-slate-900 flex items-center gap-2.5">
                                <span className="flex items-center justify-center w-7 h-7 rounded-lg bg-primary-100 text-primary-700 text-xs font-bold border border-primary-200">{resumes.length}</span>
                                Selected Candidates
                            </h3>
                            {resumes.length > 0 && (
                                <button onClick={() => setResumes([])} className="text-xs text-rose-500 hover:text-rose-700 font-bold hover:bg-rose-50 px-3 py-1.5 rounded-lg transition-colors">
                                    Clear All
                                </button>
                            )}
                        </div>

                        {resumes.length === 0 ? (
                            <div className="flex-1 flex flex-col items-center justify-center text-slate-400 py-12 border-2 border-dashed border-slate-100 rounded-2xl bg-slate-50/50">
                                <FileText className="w-16 h-16 mb-4 opacity-20" />
                                <p className="text-sm font-medium">No resumes selected yet</p>
                            </div>
                        ) : (
                            <div className="space-y-3 max-h-[500px] overflow-y-auto pr-2 custom-scrollbar">
                                {resumes.map((file, idx) => (
                                    <div key={idx} className="group relative flex items-center justify-between p-4 bg-white border border-slate-100 rounded-xl shadow-sm hover:shadow-md hover:border-primary-200 hover:translate-x-1 transition-all">
                                        <div className="flex items-center gap-4 overflow-hidden">
                                            <div className="w-10 h-10 rounded-lg bg-slate-50 flex items-center justify-center flex-shrink-0 border border-slate-100 text-slate-500 group-hover:bg-primary-50 group-hover:text-primary-600 transition-colors font-bold text-xs">
                                                PDF
                                            </div>
                                            <div className="flex flex-col min-w-0">
                                                <span className="truncate font-semibold text-sm text-slate-800">{file.name}</span>
                                                <span className="text-xs text-slate-400 font-medium">{formatBytes(file.size)}</span>
                                            </div>
                                        </div>
                                        <button
                                            onClick={() => removeFile(idx)}
                                            className="p-2 text-slate-300 hover:text-rose-500 hover:bg-rose-50 rounded-lg transition-all opacity-0 group-hover:opacity-100 focus:opacity-100"
                                        >
                                            <X className="w-4 h-4" />
                                        </button>
                                    </div>
                                ))}
                            </div>
                        )}

                        <div className="mt-8 pt-6 border-t border-slate-100">
                            {error && (
                                <div className="mb-6 p-4 rounded-xl bg-rose-50 text-rose-700 text-sm flex items-start gap-3 animate-slide-up border border-rose-100 shadow-sm">
                                    <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                                    <span>{error}</span>
                                </div>
                            )}

                            <button
                                onClick={handleAnalyze}
                                disabled={isUploading || isAnalyzing || resumes.length === 0}
                                className={cn(
                                    "w-full relative overflow-hidden group py-4 rounded-xl font-bold text-lg shadow-xl transition-all flex items-center justify-center gap-3",
                                    isUploading || isAnalyzing
                                        ? "bg-slate-100 text-slate-400 cursor-not-allowed"
                                        : "bg-primary-600 hover:bg-primary-700 text-white shadow-primary-500/30 hover:shadow-primary-600/40 hover:-translate-y-0.5 active:translate-y-0"
                                )}
                            >
                                {isUploading || isAnalyzing || resumes.length === 0 ? null : (
                                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:animate-shimmer" />
                                )}

                                {isUploading ? (
                                    <> <Loader2 className="w-6 h-6 animate-spin text-primary-600" /> <span className="text-primary-700">Uploading Files...</span> </>
                                ) : isAnalyzing ? (
                                    <> <Loader2 className="w-6 h-6 animate-spin text-primary-600" /> <span className="text-primary-700">Analyzing matches...</span> </>
                                ) : (
                                    <> Analyze {resumes.length > 0 ? `${resumes.length} Candidates` : 'Candidates'} <Sparkles className="w-5 h-5 group-hover:scale-125 transition-transform" /> </>
                                )}
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Results Section */}
            {results && (
                <div id="results-section" className="space-y-6 pt-12 border-t border-slate-200 animate-slide-up">
                    <ResultsDashboard results={results} />
                </div>
            )}
        </div>
    );
};

export default ResumeUploader;
