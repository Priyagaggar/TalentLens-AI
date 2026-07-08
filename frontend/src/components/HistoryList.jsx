import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Clock, ChevronRight, Loader2, FileText, ArrowLeft, Trash2 } from 'lucide-react';
import ResultsDashboard from './ResultsDashboard';
import { getApiBaseUrl } from '../utils';

const API_BASE_URL = getApiBaseUrl();

const HistoryList = ({ token }) => {
    const [jobs, setJobs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [selectedJobId, setSelectedJobId] = useState(null);
    const [jobResults, setJobResults] = useState(null);
    const [loadingResults, setLoadingResults] = useState(false);

    useEffect(() => {
        fetchJobs();
    }, []);

    const fetchJobs = async () => {
        try {
            setLoading(true);
            const res = await axios.get(`${API_BASE_URL}/history/jobs`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setJobs(res.data);
        } catch (err) {
            console.error(err);
            setError("Failed to load history.");
        } finally {
            setLoading(false);
        }
    };

    const loadJobResults = async (jobId) => {
        try {
            setSelectedJobId(jobId);
            setLoadingResults(true);
            const res = await axios.get(`${API_BASE_URL}/history/jobs/${jobId}/results`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setJobResults(res.data);
        } catch (err) {
            console.error(err);
            setError("Failed to load results for this job.");
            setSelectedJobId(null);
        } finally {
            setLoadingResults(false);
        }
    };

    const deleteJob = async (jobId) => {
        if (!window.confirm("Are you sure you want to delete this screening run? This will delete all associated candidates and results.")) {
            return;
        }
        try {
            await axios.delete(`${API_BASE_URL}/history/jobs/${jobId}`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setJobs(prev => prev.filter(j => j.id !== jobId));
        } catch (err) {
            console.error(err);
            alert("Failed to delete the job screening.");
        }
    };

    if (selectedJobId && jobResults) {
        return (
            <div className="space-y-6 animate-fade-in relative z-10 max-w-6xl mx-auto">
                <button 
                    onClick={() => { setSelectedJobId(null); setJobResults(null); }}
                    className="flex items-center gap-2 text-slate-500 hover:text-slate-800 font-semibold mb-4 transition-colors"
                >
                    <ArrowLeft className="w-4 h-4" /> Back to History
                </button>
                <ResultsDashboard results={jobResults} token={token} />
            </div>
        );
    }

    return (
        <div className="max-w-4xl mx-auto space-y-8 animate-fade-in relative z-10">
            <div className="text-center space-y-4 pt-8">
                <h1 className="text-3xl md:text-4xl font-display font-bold tracking-tight text-slate-900">
                    Your Screening <span className="text-primary-600">History</span>
                </h1>
                <p className="text-slate-600">Review past job descriptions and candidate rankings.</p>
            </div>

            <div className="bg-white/80 backdrop-blur-xl rounded-3xl border border-slate-200/60 shadow-xl shadow-slate-200/40 p-6 min-h-[400px]">
                {loading ? (
                    <div className="flex flex-col items-center justify-center h-64 text-slate-400">
                        <Loader2 className="w-8 h-8 animate-spin text-primary-500 mb-4" />
                        <p>Loading history...</p>
                    </div>
                ) : error ? (
                    <div className="flex flex-col items-center justify-center h-64 text-rose-500">
                        <p>{error}</p>
                        <button onClick={fetchJobs} className="mt-4 text-primary-600 underline">Try Again</button>
                    </div>
                ) : jobs.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-64 text-slate-400">
                        <Clock className="w-12 h-12 mb-4 opacity-30" />
                        <p className="font-medium text-lg">No history found</p>
                        <p className="text-sm">Run an analysis on the Dashboard to see it here.</p>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {jobs.map(job => (
                            <div 
                                key={job.id} 
                                onClick={() => loadJobResults(job.id)}
                                className="group flex items-center justify-between p-5 bg-white border border-slate-100 rounded-2xl shadow-sm hover:shadow-md hover:border-primary-200 cursor-pointer transition-all"
                            >
                                <div className="flex items-center gap-4">
                                    <div className="p-3 bg-slate-50 text-slate-400 rounded-xl group-hover:bg-primary-50 group-hover:text-primary-600 transition-colors">
                                        <FileText className="w-6 h-6" />
                                    </div>
                                    <div>
                                        <h3 className="font-bold text-slate-800 text-lg line-clamp-1">{job.title}</h3>
                                        <p className="text-xs text-slate-400 font-medium">
                                            {new Date(job.created_at).toLocaleDateString()} at {new Date(job.created_at).toLocaleTimeString()}
                                        </p>
                                    </div>
                                </div>
                                <div className="flex items-center gap-3">
                                    <button 
                                        onClick={(e) => { e.stopPropagation(); deleteJob(job.id); }}
                                        className="p-2 text-slate-400 hover:text-rose-500 hover:bg-rose-50 rounded-xl transition-colors"
                                        title="Delete Screening"
                                    >
                                        <Trash2 className="w-5 h-5" />
                                    </button>
                                    <div className="text-slate-300 group-hover:text-primary-500 transition-colors">
                                        {loadingResults && selectedJobId === job.id ? (
                                            <Loader2 className="w-6 h-6 animate-spin" />
                                        ) : (
                                            <ChevronRight className="w-6 h-6" />
                                        )}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default HistoryList;
