import React, { useState } from 'react';
import axios from 'axios';
import { ScanEye, Loader2 } from 'lucide-react';

const Auth = ({ onLogin }) => {
    const [isLogin, setIsLogin] = useState(true);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);

    const getApiBaseUrl = () => {
        let url = import.meta.env.VITE_API_URL;
        if (!url) return "/api/v1";
        if (url.endsWith('/')) url = url.slice(0, -1);
        if (!url.endsWith('/api/v1')) url += '/api/v1';
        return url;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setLoading(true);

        const formData = new URLSearchParams();
        formData.append('username', email); // OAuth2 requires 'username'
        formData.append('password', password);

        try {
            const endpoint = isLogin ? '/auth/login' : '/auth/register';
            const response = await axios.post(`${getApiBaseUrl()}${endpoint}`, formData, {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            });
            onLogin(response.data.access_token);
        } catch (err) {
            setError(err.response?.data?.detail || "Authentication failed. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex items-center justify-center h-full">
            <div className="w-full max-w-md bg-white rounded-2xl shadow-xl shadow-slate-200/50 p-8 border border-slate-100">
                <div className="flex flex-col items-center mb-8">
                    <div className="w-12 h-12 rounded-xl bg-primary-50 flex items-center justify-center text-primary-600 mb-4 shadow-sm border border-primary-100/50">
                        <ScanEye className="w-7 h-7" />
                    </div>
                    <h2 className="text-2xl font-bold text-slate-800">
                        {isLogin ? 'Welcome Back' : 'Create an Account'}
                    </h2>
                    <p className="text-slate-500 mt-2 text-sm text-center">
                        {isLogin 
                            ? 'Sign in to access your talent screening dashboard' 
                            : 'Sign up to start screening candidates with AI'}
                    </p>
                </div>

                {error && (
                    <div className="mb-6 p-3 bg-red-50 border border-red-100 rounded-lg text-red-600 text-sm font-medium text-center">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Email Address</label>
                        <input 
                            type="email" 
                            required
                            className="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all outline-none"
                            placeholder="recruiter@company.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Password</label>
                        <input 
                            type="password" 
                            required
                            className="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all outline-none"
                            placeholder="••••••••"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                        />
                    </div>
                    <button 
                        type="submit"
                        disabled={loading}
                        className="w-full mt-6 py-2.5 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg transition-colors flex items-center justify-center shadow-md shadow-primary-600/20 disabled:opacity-70 disabled:cursor-not-allowed"
                    >
                        {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : (isLogin ? 'Sign In' : 'Sign Up')}
                    </button>
                </form>

                <div className="mt-6 text-center text-sm text-slate-500">
                    {isLogin ? "Don't have an account? " : "Already have an account? "}
                    <button 
                        onClick={() => { setIsLogin(!isLogin); setError(null); }}
                        className="text-primary-600 font-semibold hover:text-primary-700 hover:underline"
                    >
                        {isLogin ? 'Sign up' : 'Sign in'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default Auth;
