import React from 'react';
import { ShieldAlert, CheckCircle2, AlertTriangle, FileText, ArrowLeft } from 'lucide-react';

interface ResultProps {
    data: any;
    onReset: () => void;
}

const ResultsView: React.FC<ResultProps> = ({ data, onReset }) => {
    const getTriageColor = (level: string) => {
        switch (level) {
            case 'EMERGENCY': return 'bg-red-500';
            case 'URGENT': return 'bg-amber-500';
            case 'ROUTINE': return 'bg-emerald-500';
            default: return 'bg-blue-500';
        }
    };

    const handleDownload = () => {
        const reportText = `
SYMPTOM INTELLIGENCE ASSESSMENT REPORT
=======================================
Date: ${new Date().toLocaleDateString()}
Triage Level: ${data.triage_level}

REASONING:
${data.reasoning}

SYMPTOMS IDENTIFIED:
${data.symptoms.map((s: any) => `- ${s.name} (${s.severity})`).join('\n')}

SAFETY ALERTS:
${data.safety_alerts.length > 0
                ? data.safety_alerts.map((a: any) => `- ${a.med_a ? `${a.med_a} + ${a.med_b}` : a.med}: ${a.risk}`).join('\n')
                : 'None identified.'}

RECOMMENDATIONS:
${data.recommendations.map((r: string) => `- ${r}`).join('\n')}

DISCLAIMER:
${data.disclaimer}
    `;

        const blob = new Blob([reportText], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Symptom_Report_${new Date().toISOString().split('T')[0]}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    };

    return (
        <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-500">
            {/* Triage Header */}
            <div className={`p-6 rounded-3xl text-white ${getTriageColor(data.triage_level)} shadow-lg shadow-opacity-20`}>
                <div className="flex items-center justify-between mb-4">
                    <span className="text-xs font-black uppercase tracking-[0.2em] opacity-80">Triage Level</span>
                    <ShieldAlert className="w-6 h-6" />
                </div>
                <h2 className="text-3xl font-black mb-1">{data.triage_level}</h2>
                <p className="text-sm font-medium opacity-90 leading-relaxed">
                    {data.reasoning}
                </p>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-2">
                <button
                    onClick={handleDownload}
                    className="flex-1 bg-slate-900 text-white font-bold py-3 rounded-2xl flex items-center justify-center gap-2 hover:bg-slate-800 transition-all text-sm"
                >
                    <FileText className="w-4 h-4" />
                    Download Report
                </button>
            </div>

            {/* Structured Symptoms */}
            <section>
                <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-3 px-1">Extracted Symptoms</h3>
                <div className="grid grid-cols-1 gap-2">
                    {data.symptoms.map((s: any, i: number) => (
                        <div key={i} className="bg-slate-50 border border-slate-100 p-3 rounded-2xl flex items-center justify-between">
                            <span className="font-bold text-slate-700">{s.name}</span>
                            <span className={`text-[10px] font-black px-2 py-0.5 rounded-full uppercase ${s.severity === 'severe' ? 'bg-red-100 text-red-600' : 'bg-slate-200 text-slate-600'
                                }`}>
                                {s.severity}
                            </span>
                        </div>
                    ))}
                </div>
            </section>

            {/* Safety Alerts */}
            {data.safety_alerts.length > 0 && (
                <section className="bg-red-50 border-2 border-red-100 rounded-2xl p-4">
                    <div className="flex items-center gap-2 mb-3 text-red-600 font-bold">
                        <AlertTriangle className="w-5 h-5" />
                        <span>Safety Warnings</span>
                    </div>
                    <ul className="space-y-2">
                        {data.safety_alerts.map((alert: any, i: number) => (
                            <li key={i} className="text-sm text-red-700 leading-tight">
                                <span className="font-bold underline">{alert.med_a ? `${alert.med_a} + ${alert.med_b}` : alert.med}:</span> {alert.risk}
                            </li>
                        ))}
                    </ul>
                </section>
            )}

            {/* Recommendations */}
            <section>
                <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-3 px-1">Clinical Protocols</h3>
                <ul className="space-y-3">
                    {data.recommendations.map((rec: string, i: number) => (
                        <li key={i} className="flex gap-3 text-slate-600">
                            <CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0" />
                            <span className="text-sm font-medium leading-normal">{rec}</span>
                        </li>
                    ))}
                </ul>
            </section>

            {/* Reset Action */}
            <button
                onClick={onReset}
                className="w-full flex items-center justify-center gap-2 py-3 text-slate-400 font-bold hover:text-primary-600 transition-colors mt-4"
            >
                <ArrowLeft className="w-4 h-4" />
                New Assessment
            </button>
        </div>
    );
};

export default ResultsView;
