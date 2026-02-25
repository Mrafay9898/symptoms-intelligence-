import React, { useState } from 'react';
import { Activity, ShieldAlert, AlertCircle } from 'lucide-react';
import SymptomInput from './components/SymptomInput';
import ResultsView from './components/ResultsView';

function App() {
    const [step, setStep] = useState<'input' | 'loading' | 'results' | 'error'>('input');
    const [analysisData, setAnalysisData] = useState<any>(null);
    const [error, setError] = useState<string | null>(null);
    const [history, setHistory] = useState<any[]>([]);

    // Load history from local storage
    React.useEffect(() => {
        const saved = localStorage.getItem('symptom_history');
        if (saved) setHistory(JSON.parse(saved));
    }, []);

    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

    const handleAnalyze = async (data: { text: string; medications: string[]; vitals: any }) => {
        setStep('loading');
        setError(null);

        try {
            const response = await fetch(`${API_URL}/analyze`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: data.text,
                    medications: data.medications,
                    vitals: data.vitals,
                    existing_conditions: [] // Expanded later
                }),
            });

            if (!response.ok) throw new Error('Failed to connect to AI Engine');

            const result = await response.json();

            // Update history
            const newEntry = { ...result, date: new Date().toISOString() };
            const updatedHistory = [newEntry, ...history].slice(0, 5);
            setHistory(updatedHistory);
            localStorage.setItem('symptom_history', JSON.stringify(updatedHistory));

            setAnalysisData(result);
            setStep('results');
        } catch (err) {
            console.error(err);
            setError('The AI Engine is currently unavailable. Please ensure the backend is running.');
            setStep('error');
        }
    };

    return (
        <div className="min-h-screen bg-slate-50 flex flex-col items-center p-4">
            {/* Header */}
            <header className="w-full max-w-md flex items-center gap-2 py-6">
                <div className="bg-primary-600 p-2 rounded-xl shadow-lg shadow-primary-500/30">
                    <Activity className="text-white w-6 h-6" />
                </div>
                <div>
                    <h1 className="text-xl font-black text-slate-900 leading-tight uppercase tracking-tight">Symptom Intelligence</h1>
                    <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest">Safe Clinical Decision Support</p>
                </div>
            </header>

            {/* Main Content Card */}
            <main className="w-full max-w-md bg-white rounded-[2.5rem] shadow-2xl shadow-slate-200/60 p-8 flex flex-col gap-6 relative overflow-hidden">
                {step === 'input' && (
                    <div className="space-y-8">
                        <SymptomInput onSubmit={handleAnalyze} />

                        {history.length > 0 && (
                            <div className="border-t border-slate-50 pt-6">
                                <h3 className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-4">Recent Assessments</h3>
                                <div className="space-y-2">
                                    {history.map((entry, i) => (
                                        <div
                                            key={i}
                                            onClick={() => { setAnalysisData(entry); setStep('results'); }}
                                            className="p-3 bg-slate-50 rounded-xl flex items-center justify-between cursor-pointer hover:bg-slate-100 transition-colors"
                                        >
                                            <div className="flex items-center gap-3">
                                                <div className={`w-2 h-2 rounded-full ${entry.triage_level === 'EMERGENCY' ? 'bg-red-500' :
                                                    entry.triage_level === 'URGENT' ? 'bg-amber-500' : 'bg-emerald-500'
                                                    }`} />
                                                <span className="text-xs font-bold text-slate-700">{entry.symptoms[0]?.name || 'Assessment'}</span>
                                            </div>
                                            <span className="text-[10px] font-medium text-slate-400">
                                                {new Date(entry.date).toLocaleDateString()}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {step === 'loading' && (
                    <div className="animate-in fade-in duration-700 text-center py-16">
                        <div className="relative w-24 h-24 mx-auto mb-8">
                            <div className="absolute inset-0 bg-primary-500 rounded-full animate-ping opacity-20"></div>
                            <div className="relative bg-white rounded-full p-6 shadow-xl border border-primary-50">
                                <Activity className="w-12 h-12 text-primary-600 animate-pulse" />
                            </div>
                        </div>
                        <h2 className="text-2xl font-black text-slate-800 mb-2">Analyzing...</h2>
                        <p className="text-slate-500 font-medium">Matching symptoms with medical protocols and checking safety interactions.</p>
                    </div>
                )}

                {step === 'results' && analysisData && (
                    <ResultsView data={analysisData} onReset={() => setStep('input')} />
                )}

                {step === 'error' && (
                    <div className="text-center py-12 animate-in zoom-in-95 duration-300">
                        <div className="bg-red-50 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6">
                            <AlertCircle className="w-8 h-8 text-red-500" />
                        </div>
                        <h2 className="text-xl font-bold text-slate-800 mb-2">Connection Error</h2>
                        <p className="text-slate-500 mb-8">{error}</p>
                        <button
                            onClick={() => setStep('input')}
                            className="bg-slate-900 text-white px-8 py-3 rounded-2xl font-bold hover:bg-slate-800 transition-all"
                        >
                            Try Again
                        </button>
                    </div>
                )}
            </main>

            {/* Footer Disclaimer */}
            <footer className="w-full max-w-md mt-auto pt-8 pb-4">
                <div className="bg-amber-50/50 backdrop-blur-sm rounded-2xl p-4 flex gap-3 border border-amber-100/50">
                    <ShieldAlert className="w-5 h-5 text-amber-600 shrink-0" />
                    <p className="text-[10px] text-amber-800/80 leading-relaxed font-medium uppercase tracking-wide">
                        <span className="font-black text-amber-900">Medical Disclaimer:</span> This tool is for hackathon demonstration. It provides protocol-based suggestions and is not a clinical diagnosis. Always consult a healthcare professional.
                    </p>
                </div>
            </footer>
        </div>
    );
}

export default App;
