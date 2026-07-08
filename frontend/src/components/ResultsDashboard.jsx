import React, { useState, useMemo, useEffect } from 'react';
import axios from 'axios';
import {
    Trophy,
    Download,
    Search,
    Filter,
    ChevronDown,
    ChevronUp,
    CheckCircle,
    AlertCircle,
    Briefcase,
    Code,
    Sparkles,
    FileText,
    Mail,
    Send,
    Loader2
} from 'lucide-react';
import { cn, getApiBaseUrl } from '../utils';

// Helper for gradient scores
const getScoreColor = (score) => {
    if (score >= 80) return "text-emerald-700 bg-emerald-50 border-emerald-200 ring-emerald-500/20";
    if (score >= 50) return "text-blue-700 bg-blue-50 border-blue-200 ring-blue-500/20";
    return "text-amber-700 bg-amber-50 border-amber-200 ring-amber-500/20";
};

const getScoreBadge = (score) => {
    if (score >= 80) return "bg-emerald-100 text-emerald-800 border-emerald-200";
    if (score >= 50) return "bg-blue-100 text-blue-800 border-blue-200";
    return "bg-amber-100 text-amber-800 border-amber-200";
};

const Modal = ({ title, isOpen, onClose, children }) => {
    if (!isOpen) return null;
    return (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-3xl w-full max-w-3xl max-h-[80vh] flex flex-col shadow-2xl border border-slate-100 overflow-hidden">
                <div className="p-6 border-b border-slate-100 flex items-center justify-between">
                    <h2 className="text-xl font-bold text-slate-800">{title}</h2>
                    <button 
                        onClick={onClose}
                        className="text-slate-400 hover:text-slate-600 font-semibold p-2 hover:bg-slate-50 rounded-full transition-all"
                    >
                        ✕
                    </button>
                </div>
                <div className="p-6 overflow-y-auto flex-1 text-slate-600 text-sm leading-relaxed whitespace-pre-wrap font-sans bg-slate-50">
                    {children}
                </div>
            </div>
        </div>
    );
};

const ResultsDashboard = ({ results, token }) => {
    const [minScore, setMinScore] = useState(0);
    const [minExp, setMinExp] = useState(0);
    const [skillFilter, setSkillFilter] = useState('');
    const [expandedId, setExpandedId] = useState(null);
    const [viewingJd, setViewingJd] = useState(null);
    const [viewingResume, setViewingResume] = useState(null);

    // Email dispatch state
    const [selectedIds, setSelectedIds] = useState([]);
    const [isEmailModalOpen, setIsEmailModalOpen] = useState(false);
    const [interviewThreshold, setInterviewThreshold] = useState(80);
    const [rejectionThreshold, setRejectionThreshold] = useState(50);
    const [sendingEmails, setSendingEmails] = useState(false);
    const [emailReport, setEmailReport] = useState(null);

    const candidates = results?.ranked_candidates || [];

    // Automatically select all candidates on load
    useEffect(() => {
        if (candidates.length > 0) {
            setSelectedIds(candidates.map(c => c.resume_id));
        }
    }, [candidates]);

    const toggleSelectCandidate = (resumeId) => {
        setSelectedIds(prev => 
            prev.includes(resumeId) 
                ? prev.filter(id => id !== resumeId) 
                : [...prev, resumeId]
        );
    };

    const handleToggleSelectAll = () => {
        const visibleIds = filteredCandidates.map(c => c.resume_id);
        const allVisibleSelected = visibleIds.every(id => selectedIds.includes(id));
        
        if (allVisibleSelected) {
            setSelectedIds(prev => prev.filter(id => !visibleIds.includes(id)));
        } else {
            setSelectedIds(prev => [...new Set([...prev, ...visibleIds])]);
        }
    };

    const handleSendEmails = async () => {
        if (selectedIds.length === 0) return;
        setSendingEmails(true);
        setEmailReport(null);
        try {
            const jobId = results?.job_description_id;
            if (!jobId) {
                alert("Job Description ID not found in results. Cannot send emails.");
                return;
            }
            const res = await axios.post(`${getApiBaseUrl()}/history/jobs/${jobId}/email`, {
                interview_threshold: Number(interviewThreshold),
                rejection_threshold: Number(rejectionThreshold),
                candidate_ids: selectedIds
            }, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setEmailReport(res.data);
        } catch (err) {
            console.error(err);
            alert(err.response?.data?.detail || "Failed to dispatch batch emails.");
        } finally {
            setSendingEmails(false);
        }
    };

    // Filter Logic
    const filteredCandidates = useMemo(() => {
        return candidates.filter(c => {
            const scorePass = c.final_score >= minScore;
            const expPass = c.experience_years >= minExp;
            const skillPass = skillFilter
                ? c.matched_skills.some(s => s.toLowerCase().includes(skillFilter.toLowerCase()))
                : true;
            return scorePass && expPass && skillPass;
        });
    }, [candidates, minScore, minExp, skillFilter]);

    // Export CSV
    const handleExport = () => {
        const headers = ["Rank", "Name", "Score", "Experience", "Skills Match %", "Matched Skills", "Missing Skills"];
        const rows = filteredCandidates.map((c, idx) => [
            idx + 1,
            c.name,
            c.final_score.toFixed(1),
            c.experience_years,
            c.skill_match_percentage + "%",
            c.matched_skills.join(", "),
            c.missing_skills.join(", ")
        ]);

        const csvContent = "data:text/csv;charset=utf-8,"
            + [headers.join(","), ...rows.map(e => e.map(i => `"${i}"`).join(","))].join("\n");

        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", "resume_analysis_results.csv");
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    const toggleExpand = (id) => {
        setExpandedId(expandedId === id ? null : id);
    };

    return (
        <div className="space-y-8 animate-slide-up pb-20">
            {/* Control Bar */}
            <div className="bg-white/70 backdrop-blur-xl rounded-3xl border border-white/50 p-6 shadow-xl shadow-slate-200/40 sticky top-24 z-40 transition-all">
                <div className="flex flex-col xl:flex-row xl:items-end justify-between gap-8">

                    {/* Filters */}
                    <div className="flex-1 grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="space-y-3">
                            <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest flex items-center justify-between">
                                Min Score <span className="text-primary-600">{minScore}%</span>
                            </label>
                            <input
                                type="range"
                                min="0"
                                max="100"
                                value={minScore}
                                onChange={(e) => setMinScore(Number(e.target.value))}
                                className="w-full h-2 bg-slate-100 rounded-lg appearance-none cursor-pointer accent-primary-600 hover:accent-primary-700 transition-all"
                            />
                        </div>

                        <div className="space-y-3">
                            <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest flex items-center justify-between">
                                Min Experience <span className="text-primary-600">{minExp} years</span>
                            </label>
                            <div className="relative">
                                <input
                                    type="number"
                                    min="0"
                                    max="20"
                                    value={minExp}
                                    onChange={(e) => setMinExp(Number(e.target.value))}
                                    className="w-full px-4 py-2.5 text-sm font-medium border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all bg-slate-50/50 focus:bg-white text-slate-700"
                                />
                                <span className="absolute right-3 top-2.5 text-xs font-bold text-slate-400 pointer-events-none">YRS</span>
                            </div>
                        </div>

                        <div className="space-y-3">
                            <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Filter by Skill</label>
                            <div className="relative group">
                                <Search className="absolute left-3.5 top-3 w-4 h-4 text-slate-400 group-focus-within:text-primary-500 transition-colors" />
                                <input
                                    type="text"
                                    placeholder="e.g. Python, React..."
                                    value={skillFilter}
                                    onChange={(e) => setSkillFilter(e.target.value)}
                                    className="w-full pl-10 pr-4 py-2.5 text-sm font-medium border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all bg-slate-50/50 focus:bg-white text-slate-700"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-3">
                        {results?.job_description_content && (
                            <button
                                onClick={() => setViewingJd(results.job_description_content)}
                                className="flex items-center gap-2 px-5 py-3 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 rounded-xl transition-all shadow-sm text-sm font-bold tracking-wide"
                            >
                                <FileText className="w-4 h-4 text-slate-400" /> View Job Description
                            </button>
                        )}
                        <button
                            onClick={() => { setIsEmailModalOpen(true); setEmailReport(null); }}
                            disabled={selectedIds.length === 0}
                            className="flex items-center gap-2 px-5 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl transition-all shadow-lg shadow-indigo-600/20 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-bold tracking-wide"
                        >
                            <Mail className="w-4 h-4" /> Email Candidates ({selectedIds.length})
                        </button>
                        <button
                            onClick={handleExport}
                            className="flex items-center gap-2 px-6 py-3 bg-slate-900 hover:bg-slate-800 text-white rounded-xl transition-all shadow-lg shadow-slate-900/20 hover:shadow-slate-900/30 hover:-translate-y-0.5 active:translate-y-0 text-sm font-bold tracking-wide"
                        >
                            <Download className="w-4 h-4" /> Export CSV
                        </button>
                    </div>
                </div>
            </div>

            {/* Results Grid */}
            <div className="grid gap-6">
                <div className="flex items-center justify-between text-sm text-slate-500 px-2 font-medium">
                    <div className="flex items-center gap-3">
                        <input 
                            type="checkbox"
                            checked={filteredCandidates.length > 0 && filteredCandidates.every(c => selectedIds.includes(c.resume_id))}
                            ref={(el) => {
                                if (el) {
                                    const allSelected = filteredCandidates.length > 0 && filteredCandidates.every(c => selectedIds.includes(c.resume_id));
                                    const someSelected = filteredCandidates.some(c => selectedIds.includes(c.resume_id));
                                    el.indeterminate = someSelected && !allSelected;
                                }
                            }}
                            onChange={handleToggleSelectAll}
                            className="w-4 h-4 rounded border-slate-300 text-primary-600 focus:ring-primary-500 cursor-pointer"
                        />
                        <span>Selected <span className="text-slate-900 font-bold">{filteredCandidates.filter(c => selectedIds.includes(c.resume_id)).length}</span> / {filteredCandidates.length} candidates</span>
                    </div>
                    <span className="flex items-center gap-1 cursor-pointer hover:text-primary-600 transition-colors">
                        Sort by Rank <ChevronDown className="w-3 h-3" />
                    </span>
                </div>

                {filteredCandidates.map((cand, idx) => (
                    <div
                        key={cand.resume_id}
                        className={cn(
                            "bg-white rounded-[24px] border transition-all duration-300 overflow-hidden relative group",
                            expandedId === cand.resume_id
                                ? "border-primary-200 shadow-xl shadow-primary-900/5 ring-4 ring-primary-50/50"
                                : "border-slate-100 shadow-sm hover:shadow-lg hover:shadow-slate-200/50 hover:border-primary-100 hovering-scale"
                        )}
                    >
                        {/* Rank Marker */}
                        <div className={cn(
                            "absolute top-0 left-0 px-4 py-1.5 rounded-br-2xl text-[10px] font-extrabold uppercase tracking-widest border-r border-b transition-colors z-20 flex items-center gap-2",
                            idx === 0 ? "bg-yellow-50 text-yellow-700 border-yellow-100" :
                                idx === 1 ? "bg-slate-100 text-slate-600 border-slate-200" :
                                    idx === 2 ? "bg-orange-50 text-orange-700 border-orange-100" :
                                        "bg-slate-50 text-slate-500 border-slate-100"
                        )}>
                            <input 
                                type="checkbox"
                                checked={selectedIds.includes(cand.resume_id)}
                                onChange={(e) => {
                                    e.stopPropagation();
                                    toggleSelectCandidate(cand.resume_id);
                                }}
                                className="w-3 h-3 rounded border-slate-300 text-primary-600 focus:ring-primary-500 cursor-pointer"
                            />
                            <span>Rank #{idx + 1}</span>
                        </div>

                        <div
                            className="p-6 pt-10 md:p-8 flex flex-col md:flex-row gap-8 cursor-pointer relative"
                            onClick={() => toggleExpand(cand.resume_id)}
                        >
                            <div className="absolute top-6 right-6 text-slate-300 group-hover:text-primary-400 transition-colors md:hidden">
                                {expandedId === cand.resume_id ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                            </div>

                            {/* Avatar/Score Circle */}
                            <div className="flex-shrink-0 flex flex-col items-center gap-3">
                                <div className={cn(
                                    "w-20 h-20 rounded-2xl flex items-center justify-center text-3xl font-display font-bold border-4 shadow-sm transition-all group-hover:scale-105",
                                    getScoreColor(cand.final_score)
                                )}>
                                    {cand.final_score.toFixed(0)}<span className="text-sm align-top mt-2 opacity-60">%</span>
                                </div>
                                <span className={cn("text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full border", getScoreBadge(cand.final_score))}>
                                    Match Score
                                </span>
                            </div>

                            {/* Main Info */}
                            <div className="flex-grow space-y-4">
                                <div>
                                    <h3 className="text-2xl font-display font-bold text-slate-900 group-hover:text-primary-700 transition-colors mb-2">{cand.name}</h3>

                                    <div className="flex flex-wrap gap-3 text-sm text-slate-600">
                                        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-50 border border-slate-100 font-medium">
                                            <Briefcase className="w-4 h-4 text-slate-400" />
                                            <span>{cand.experience_years} Years Exp.</span>
                                        </div>
                                        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-50 border border-slate-100 font-medium">
                                            <Code className="w-4 h-4 text-slate-400" />
                                            <span>{cand.skill_match_percentage}% Skills</span>
                                        </div>
                                        {cand.resume_text && (
                                            <button 
                                                onClick={(e) => { e.stopPropagation(); setViewingResume({ name: cand.name, text: cand.resume_text }); }}
                                                className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-primary-50 hover:bg-primary-100 border border-primary-100 text-primary-700 font-semibold transition-colors"
                                            >
                                                <FileText className="w-4 h-4 text-primary-500" />
                                                <span>View Resume</span>
                                            </button>
                                        )}
                                    </div>
                                </div>

                                {/* Skills Preview (Collapsed) */}
                                {!expandedId && (
                                    <div className="flex flex-wrap gap-2 pt-1">
                                        {cand.matched_skills.slice(0, 4).map(skill => (
                                            <span key={skill} className="text-xs px-2.5 py-1 rounded-md bg-emerald-50 text-emerald-700 border border-emerald-100 font-medium">
                                                {skill}
                                            </span>
                                        ))}
                                        {cand.matched_skills.length > 4 && (
                                            <span className="text-xs text-slate-400 px-2 flex items-center font-medium">+{cand.matched_skills.length - 4} more skills</span>
                                        )}
                                    </div>
                                )}
                            </div>

                            {/* Toggle Arrow (Desktop) */}
                            <div className="hidden md:flex flex-col items-end justify-center pl-4">
                                <div className={cn(
                                    "p-2 rounded-full border transition-all duration-300",
                                    expandedId === cand.resume_id
                                        ? "bg-primary-50 text-primary-600 border-primary-100 rotate-180"
                                        : "bg-white text-slate-300 border-slate-100 group-hover:border-primary-200 group-hover:text-primary-400"
                                )}>
                                    <ChevronDown className="w-5 h-5" />
                                </div>
                            </div>
                        </div>

                        {/* Expandable Content */}
                        <div
                            className={cn(
                                "grid transition-all duration-500 ease-[cubic-bezier(0.4,0,0.2,1)]",
                                expandedId === cand.resume_id ? "grid-rows-[1fr] opacity-100" : "grid-rows-[0fr] opacity-0"
                            )}
                        >
                            <div className="overflow-hidden">
                                <div className="px-6 md:px-8 pb-8 pt-2 border-t border-slate-100 bg-slate-50/50">

                                    {/* AI Explanation Box */}
                                    <div className="mb-8 mt-6 relative">
                                        <div className="absolute -inset-0.5 bg-gradient-to-r from-primary-100 to-indigo-100 rounded-2xl blur opacity-30"></div>
                                        <div className="relative p-6 bg-white rounded-xl border border-primary-100/50 text-sm text-slate-600 leading-relaxed shadow-sm">
                                            <div className="flex items-center gap-2 mb-3 font-bold text-primary-700">
                                                <Sparkles className="w-4 h-4 fill-primary-100" /> AI Selection Logic
                                            </div>
                                            <div className="space-y-2 pl-1 border-l-2 border-primary-100">
                                                {cand.explanation.split('\n').map((line, i) => (
                                                    <p key={i} className="pl-4">{line}</p>
                                                ))}
                                            </div>
                                        </div>
                                    </div>

                                    <div className="grid md:grid-cols-2 gap-8">
                                        {/* Matched Skills */}
                                        <div>
                                            <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                                                <CheckCircle className="w-4 h-4 text-emerald-500" /> Matched Skills
                                            </h4>
                                            <div className="flex flex-wrap gap-2">
                                                {cand.matched_skills.length > 0 ? cand.matched_skills.map(skill => (
                                                    <span key={skill} className="px-3 py-1 bg-white text-emerald-700 text-xs font-bold rounded-lg border border-emerald-100 shadow-sm">
                                                        {skill}
                                                    </span>
                                                )) : <span className="text-sm text-slate-500 italic">No exact skill matches found.</span>}
                                            </div>
                                        </div>

                                        {/* Missing Skills */}
                                        <div>
                                            <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                                                <AlertCircle className="w-4 h-4 text-rose-500" /> Missing Skills
                                            </h4>
                                            <div className="flex flex-wrap gap-2">
                                                {cand.missing_skills.length > 0 ? cand.missing_skills.map(skill => (
                                                    <span key={skill} className="px-3 py-1 bg-white text-rose-600 text-xs font-bold rounded-lg border border-red-100 shadow-sm opacity-90 dashed-border">
                                                        {skill}
                                                    </span>
                                                )) : <div className="flex items-center gap-2 text-sm text-emerald-600 font-bold bg-emerald-50 px-3 py-2 rounded-lg border border-emerald-100 self-start inline-flex"><CheckCircle className="w-4 h-4" /> Perfect Skill Match!</div>}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                ))}

                {filteredCandidates.length === 0 && (
                    <div className="text-center py-24 bg-white/40 backdrop-blur rounded-[24px] border border-dashed border-slate-300">
                        <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
                            <Filter className="w-6 h-6 text-slate-400" />
                        </div>
                        <h3 className="text-lg font-bold text-slate-900">No matches found</h3>
                        <p className="text-slate-500 mt-1 mb-6 max-w-xs mx-auto">None of the candidates match your current filter criteria.</p>
                        <button
                            onClick={() => { setMinScore(0); setMinExp(0); setSkillFilter(''); }}
                            className="px-5 py-2.5 bg-white border border-slate-200 shadow-sm text-slate-700 rounded-xl hover:bg-slate-50 font-bold text-sm transition-all hover:border-slate-300"
                        >
                            Reset All Filters
                        </button>
                    </div>
                )}
            </div>

            {/* Modals */}
            <Modal 
                title="Original Job Description" 
                isOpen={viewingJd !== null} 
                onClose={() => setViewingJd(null)}
            >
                {viewingJd}
            </Modal>

            <Modal 
                title={`Resume: ${viewingResume?.name || ''}`}
                isOpen={viewingResume !== null} 
                onClose={() => setViewingResume(null)}
            >
                {viewingResume?.text}
            </Modal>

            {/* Email Dispatch Modal */}
            <Modal
                title={`Email Selected Candidates (${selectedIds.length})`}
                isOpen={isEmailModalOpen}
                onClose={() => { if (!sendingEmails) setIsEmailModalOpen(false); }}
            >
                {!emailReport ? (
                    <div className="space-y-6">
                        <p className="text-slate-500 text-sm">
                            Configure thresholds to tailor the automated email templates. Candidates will receive styled HTML notifications based on their score.
                        </p>

                        <div className="grid md:grid-cols-2 gap-8">
                            {/* Controls */}
                            <div className="space-y-6">
                                <div className="space-y-2">
                                    <label className="text-xs font-bold text-slate-500 uppercase tracking-wide flex justify-between">
                                        Interview Invite Threshold <span className="text-indigo-600 font-bold">{interviewThreshold}%</span>
                                    </label>
                                    <input 
                                        type="range"
                                        min={rejectionThreshold + 1}
                                        max="100"
                                        value={interviewThreshold}
                                        onChange={(e) => setInterviewThreshold(Number(e.target.value))}
                                        className="w-full h-2 bg-slate-100 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                                    />
                                </div>

                                <div className="space-y-2">
                                    <label className="text-xs font-bold text-slate-500 uppercase tracking-wide flex justify-between">
                                        Rejection Threshold <span className="text-rose-600 font-bold">{rejectionThreshold}%</span>
                                    </label>
                                    <input 
                                        type="range"
                                        min="0"
                                        max={interviewThreshold - 1}
                                        value={rejectionThreshold}
                                        onChange={(e) => setRejectionThreshold(Number(e.target.value))}
                                        className="w-full h-2 bg-slate-100 rounded-lg appearance-none cursor-pointer accent-rose-600"
                                    />
                                </div>
                            </div>

                            {/* Preview Panel */}
                            <div className="bg-slate-50 p-5 rounded-2xl border border-slate-200/60 space-y-4">
                                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Email Dispatch Preview</h4>
                                <div className="space-y-3">
                                    <div className="flex justify-between items-center text-sm font-medium text-slate-600">
                                        <span className="flex items-center gap-2"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500" /> Interview Invitations:</span>
                                        <span className="font-bold text-slate-800">
                                            {candidates.filter(c => selectedIds.includes(c.resume_id) && c.final_score >= interviewThreshold).length}
                                        </span>
                                    </div>
                                    <div className="flex justify-between items-center text-sm font-medium text-slate-600">
                                        <span className="flex items-center gap-2"><span className="w-2.5 h-2.5 rounded-full bg-slate-400" /> Keep in Touch/Hold:</span>
                                        <span className="font-bold text-slate-800">
                                            {selectedIds.length - 
                                             candidates.filter(c => selectedIds.includes(c.resume_id) && c.final_score >= interviewThreshold).length - 
                                             candidates.filter(c => selectedIds.includes(c.resume_id) && c.final_score < rejectionThreshold).length}
                                        </span>
                                    </div>
                                    <div className="flex justify-between items-center text-sm font-medium text-slate-600">
                                        <span className="flex items-center gap-2"><span className="w-2.5 h-2.5 rounded-full bg-rose-500" /> Polite Rejections:</span>
                                        <span className="font-bold text-slate-800">
                                            {candidates.filter(c => selectedIds.includes(c.resume_id) && c.final_score < rejectionThreshold).length}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="flex justify-end gap-3 pt-4 border-t border-slate-100">
                            <button
                                onClick={() => setIsEmailModalOpen(false)}
                                disabled={sendingEmails}
                                className="px-5 py-2.5 bg-white border border-slate-200 text-slate-700 rounded-xl hover:bg-slate-50 font-bold text-sm transition-all"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleSendEmails}
                                disabled={sendingEmails}
                                className="flex items-center gap-2 px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-bold text-sm transition-all shadow-md shadow-indigo-600/20 disabled:opacity-75 disabled:cursor-not-allowed"
                            >
                                {sendingEmails ? (
                                    <>
                                        <Loader2 className="w-4 h-4 animate-spin" />
                                        Sending...
                                    </>
                                ) : (
                                    <>
                                        <Send className="w-4 h-4" />
                                        Send Emails
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                ) : (
                    // Email Dispatch Report (Detailed summary)
                    <div className="space-y-6">
                        <div className="flex items-center gap-3 p-4 bg-emerald-50 border border-emerald-100 rounded-2xl text-emerald-800">
                            <CheckCircle className="w-6 h-6 text-emerald-500" />
                            <div>
                                <h4 className="font-bold text-sm">Batch Email Dispatch Completed</h4>
                                <p className="text-xs opacity-90">
                                    Successfully delivered {emailReport.successful_count} emails. Failed to deliver {emailReport.failed_count} emails.
                                </p>
                            </div>
                        </div>

                        {emailReport.failed_count > 0 && (
                            <div className="space-y-3">
                                <h4 className="text-xs font-bold text-rose-600 uppercase tracking-wider flex items-center gap-2">
                                    <AlertCircle className="w-4 h-4" /> Failed Dispatches ({emailReport.failed_count})
                                </h4>
                                <div className="max-h-40 overflow-y-auto border border-rose-100 rounded-xl bg-rose-50/20 divide-y divide-rose-100/50">
                                    {emailReport.failures.map((f, i) => (
                                        <div key={i} className="p-3 text-xs flex justify-between items-center">
                                            <div>
                                                <span className="font-bold text-slate-800">{f.name}</span>
                                                <span className="text-slate-400 ml-2">({f.email})</span>
                                            </div>
                                            <span className="text-rose-600 font-semibold">{f.reason}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        <div className="flex justify-end pt-4 border-t border-slate-100">
                            <button
                                onClick={() => setIsEmailModalOpen(false)}
                                className="px-6 py-2.5 bg-slate-900 hover:bg-slate-800 text-white rounded-xl font-bold text-sm transition-all shadow-md"
                            >
                                Close
                            </button>
                        </div>
                    </div>
                )}
            </Modal>
        </div>
    );
};

export default ResultsDashboard;
