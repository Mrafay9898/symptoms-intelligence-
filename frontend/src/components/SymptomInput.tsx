import React, { useState } from 'react';
import { Pill, Activity, Plus, X, Thermometer, ShieldAlert, Mic } from 'lucide-react';

interface SymptomInputProps {
    onSubmit: (data: { text: string; medications: string[]; vitals: Record<string, string> }) => void;
}

const SymptomInput: React.FC<SymptomInputProps> = ({ onSubmit }) => {
    const [text, setText] = useState('');
    const [meds, setMeds] = useState<string[]>([]);
    const [currentMed, setCurrentMed] = useState('');
    const [vitals, setVitals] = useState({ temp: '', hr: '', bp: '' });
    const [isListening, setIsListening] = useState(false);

    const addMed = () => {
        if (currentMed.trim()) {
            setMeds([...meds, currentMed.trim()]);
            setCurrentMed('');
        }
    };

    const removeMed = (index: number) => {
        setMeds(meds.filter((_, i) => i !== index));
    };

    const startListening = () => {
        const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
        if (!SpeechRecognition) {
            alert('Your browser does not support speech recognition. Please try Chrome or Edge.');
            return;
        }

        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onstart = () => setIsListening(true);
        recognition.onend = () => setIsListening(false);
        recognition.onresult = (event: any) => {
            const transcript = event.results[0][0].transcript;
            setText((prev) => prev ? `${prev} ${transcript}` : transcript);
        };

        recognition.start();
    };

    return (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div>
                <div className="flex justify-between items-center mb-2">
                    <h2 className="text-2xl font-bold text-slate-800">Describe symptoms</h2>
                    <button
                        onClick={startListening}
                        className={`p-2 rounded-full transition-all ${isListening ? 'bg-red-100 text-red-600 animate-pulse' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}`}
                        title="Voice Input"
                    >
                        <Mic className={`w-5 h-5 ${isListening ? 'fill-current' : ''}`} />
                    </button>
                </div>
                <textarea
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    className="w-full h-28 p-4 rounded-2xl border-2 border-slate-100 focus:border-primary-500 focus:outline-none transition-all resize-none shadow-inner bg-slate-50/50"
                    placeholder="e.g. Sharp abdominal pain..."
                />
            </div>

            {/* Vitals Section */}
            <div className="grid grid-cols-3 gap-3">
                <div className="space-y-1">
                    <label className="text-[10px] font-black text-slate-400 uppercase tracking-tighter flex items-center gap-1">
                        <Thermometer className="w-3 h-3" /> Temp
                    </label>
                    <input
                        type="text"
                        placeholder="98.6°F"
                        value={vitals.temp}
                        onChange={(e) => setVitals({ ...vitals, temp: e.target.value })}
                        className="w-full px-3 py-2 rounded-xl border border-slate-200 focus:ring-2 focus:ring-primary-100 text-sm font-bold"
                    />
                </div>
                <div className="space-y-1">
                    <label className="text-[10px] font-black text-slate-400 uppercase tracking-tighter flex items-center gap-1">
                        <Activity className="w-3 h-3" /> HR
                    </label>
                    <input
                        type="text"
                        placeholder="72 bpm"
                        value={vitals.hr}
                        onChange={(e) => setVitals({ ...vitals, hr: e.target.value })}
                        className="w-full px-3 py-2 rounded-xl border border-slate-200 focus:ring-2 focus:ring-primary-100 text-sm font-bold"
                    />
                </div>
                <div className="space-y-1">
                    <label className="text-[10px] font-black text-slate-400 uppercase tracking-tighter flex items-center gap-1">
                        <ShieldAlert className="w-3 h-3" /> BP
                    </label>
                    <input
                        type="text"
                        placeholder="120/80"
                        value={vitals.bp}
                        onChange={(e) => setVitals({ ...vitals, bp: e.target.value })}
                        className="w-full px-3 py-2 rounded-xl border border-slate-200 focus:ring-2 focus:ring-primary-100 text-sm font-bold"
                    />
                </div>
            </div>

            <div className="space-y-3">
                <label className="flex items-center gap-2 text-[10px] font-black text-slate-400 uppercase tracking-wider">
                    <Pill className="w-4 h-4 text-primary-500" /> Medications
                </label>
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={currentMed}
                        onChange={(e) => setCurrentMed(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && addMed()}
                        placeholder="Add medication..."
                        className="flex-1 px-4 py-2 rounded-xl border border-slate-200 focus:ring-2 focus:ring-primary-100"
                    />
                    <button onClick={addMed} className="p-2 bg-primary-100 text-primary-600 rounded-xl hover:bg-primary-200 transition-colors">
                        <Plus className="w-6 h-6" />
                    </button>
                </div>
                <div className="flex flex-wrap gap-2 min-h-[40px]">
                    {meds.map((med, i) => (
                        <span key={i} className="bg-white border border-slate-100 px-3 py-1 rounded-full text-xs font-bold text-slate-600 flex items-center gap-2 shadow-sm">
                            {med}
                            <X className="w-3 h-3 cursor-pointer text-slate-400 hover:text-red-500" onClick={() => removeMed(i)} />
                        </span>
                    ))}
                </div>
            </div>

            <button
                onClick={() => onSubmit({ text, medications: meds, vitals })}
                disabled={!text.trim()}
                className="w-full bg-primary-600 hover:bg-primary-700 disabled:bg-slate-300 text-white font-bold py-4 rounded-2xl shadow-lg flex items-center justify-center gap-2 transition-all active:scale-95"
            >
                <Activity className="w-5 h-5" />
                Analyze Health Data
            </button>
        </div>
    );
};

export default SymptomInput;
