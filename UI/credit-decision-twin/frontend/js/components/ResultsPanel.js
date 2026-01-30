// Results Panel Component - displays decision, twins, anomaly radar, and explanation

function DecisionBanner({ decision, anomalyScore }) {
    if (!decision) return null;
    
    const statusClass = decision.decision === 'APPROVE' ? 'status-approve' : 
                        decision.decision === 'CONDITIONAL' ? 'status-conditional' : 'status-decline';
    const icon = decision.decision === 'APPROVE' ? '✅' : 
                 decision.decision === 'CONDITIONAL' ? '⚠️' : '❌';
    const anomalyLevel = anomalyScore < 0.3 ? 'LOW' : anomalyScore < 0.6 ? 'MED' : 'HIGH';
    
    return (
        <div className={`rounded-xl p-6 card-glow text-white ${statusClass}`}>
            <div className="flex items-center justify-between flex-wrap gap-4">
                <div className="flex items-center gap-4">
                    <div className="w-16 h-16 rounded-full flex items-center justify-center text-3xl bg-white/20">
                        {icon}
                    </div>
                    <div>
                        <p className="text-sm opacity-80">Credit Decision</p>
                        <h2 className="text-2xl font-bold">{decision.decision}</h2>
                        <p className="text-sm opacity-80 mt-1">{decision.reason}</p>
                    </div>
                </div>
                <div className="grid grid-cols-3 gap-4">
                    <div className="bg-white/10 rounded-lg px-4 py-2 text-center">
                        <p className="text-xs opacity-70">Confidence</p>
                        <p className="text-xl font-bold">{(decision.confidence * 100).toFixed(0)}%</p>
                    </div>
                    <div className="bg-white/10 rounded-lg px-4 py-2 text-center">
                        <p className="text-xs opacity-70">Risk Tier</p>
                        <p className="text-xl font-bold">{decision.risk_tier}</p>
                    </div>
                    <div className="bg-white/10 rounded-lg px-4 py-2 text-center">
                        <p className="text-xs opacity-70">Anomaly</p>
                        <p className="text-xl font-bold">{anomalyLevel}</p>
                    </div>
                </div>
            </div>
        </div>
    );
}

function TwinsList({ twins }) {
    return (
        <div className="bg-slate-800 rounded-xl p-6 card-glow">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <span className="w-8 h-8 bg-purple-500/20 rounded-lg flex items-center justify-center text-purple-400">2</span>
                Financial Twins (Top 10)
            </h2>
            <p className="text-xs text-slate-400 mb-4">Most similar historical borrowers from Qdrant vector search</p>
            <div className="space-y-2 max-h-80 overflow-y-auto scrollbar-thin pr-2">
                {twins.slice(0, 10).map((twin, i) => (
                    <div key={twin.id} className="twin-card bg-slate-700/50 rounded-lg p-3 cursor-pointer hover:bg-slate-700">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${twin.outcome === 'REPAID' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                                    {i + 1}
                                </div>
                                <div>
                                    <p className="text-sm font-medium">{twin.id}</p>
                                    <p className="text-xs text-slate-400">Score: {twin.credit_score} | Income: ${twin.income.toLocaleString()}</p>
                                </div>
                            </div>
                            <div className="text-right">
                                <p className={`text-sm font-bold ${twin.outcome === 'REPAID' ? 'text-green-400' : 'text-red-400'}`}>{twin.outcome}</p>
                                <p className="text-xs text-slate-400">{(twin.similarity * 100).toFixed(1)}% similar</p>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

function AnomalyRadar({ twins, anomalyScore, flags }) {
    const maxSim = twins[0]?.similarity || 0;
    const avgSim = twins.reduce((sum, t) => sum + t.similarity, 0) / twins.length;
    const decayRate = twins.length > 9 ? (twins[0].similarity - twins[9].similarity) : 0;
    
    React.useEffect(() => {
        // Animate bars after mount
        const timer = setTimeout(() => {
            const maxSimBar = document.getElementById('maxSimBar');
            const densityBar = document.getElementById('densityBar');
            const decayBar = document.getElementById('decayBar');
            const anomalyBar = document.getElementById('anomalyBar');
            
            if (maxSimBar) maxSimBar.style.width = `${maxSim * 100}%`;
            if (densityBar) densityBar.style.width = `${avgSim * 100}%`;
            if (decayBar) decayBar.style.width = `${Math.min(100, decayRate * 200)}%`;
            if (anomalyBar) anomalyBar.style.width = `${anomalyScore * 100}%`;
        }, 100);
        return () => clearTimeout(timer);
    }, [maxSim, avgSim, decayRate, anomalyScore]);
    
    return (
        <div className="bg-slate-800 rounded-xl p-6 card-glow">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <span className="w-8 h-8 bg-orange-500/20 rounded-lg flex items-center justify-center text-orange-400">3</span>
                Risk Anomaly Radar
            </h2>
            <p className="text-xs text-slate-400 mb-4">Density and typicality analysis in vector space</p>
            <div className="space-y-4">
                <div>
                    <div className="flex justify-between text-sm mb-1">
                        <span className="text-slate-400">Max Similarity Score</span>
                        <span className="font-medium">{(maxSim * 100).toFixed(1)}%</span>
                    </div>
                    <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                        <div id="maxSimBar" className="anomaly-bar h-full bg-gradient-to-r from-green-500 to-emerald-400 rounded-full" style={{width: '0%'}}></div>
                    </div>
                </div>
                <div>
                    <div className="flex justify-between text-sm mb-1">
                        <span className="text-slate-400">Neighborhood Density</span>
                        <span className="font-medium">{(avgSim * 100).toFixed(1)}%</span>
                    </div>
                    <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                        <div id="densityBar" className="anomaly-bar h-full bg-gradient-to-r from-blue-500 to-cyan-400 rounded-full" style={{width: '0%'}}></div>
                    </div>
                </div>
                <div>
                    <div className="flex justify-between text-sm mb-1">
                        <span className="text-slate-400">Similarity Decay Rate</span>
                        <span className="font-medium">{(decayRate * 100).toFixed(1)}%</span>
                    </div>
                    <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                        <div id="decayBar" className="anomaly-bar h-full bg-gradient-to-r from-yellow-500 to-orange-400 rounded-full" style={{width: '0%'}}></div>
                    </div>
                </div>
                <div className="pt-2 border-t border-slate-700">
                    <div className="flex justify-between text-sm mb-1">
                        <span className="text-slate-400 font-medium">Overall Anomaly Score</span>
                        <span className="font-bold text-orange-400">{(anomalyScore * 100).toFixed(0)}%</span>
                    </div>
                    <div className="h-3 bg-slate-700 rounded-full overflow-hidden">
                        <div id="anomalyBar" className="anomaly-bar h-full bg-gradient-to-r from-orange-500 to-red-500 rounded-full" style={{width: '0%'}}></div>
                    </div>
                </div>
                <div className="mt-4 space-y-2">
                    {flags.length > 0 ? flags.map((flag, i) => (
                        <div key={i} className={`flex items-start gap-2 text-sm ${flag.type === 'alert' ? 'text-red-400' : flag.type === 'warning' ? 'text-yellow-400' : 'text-blue-400'}`}>
                            <span>{flag.type === 'alert' ? '🚨' : flag.type === 'warning' ? '⚠️' : 'ℹ️'}</span>
                            <span>{flag.text}</span>
                        </div>
                    )) : (
                        <p className="text-sm text-green-400">✓ No anomaly flags detected</p>
                    )}
                </div>
            </div>
        </div>
    );
}

function CohortCharts({ twins, decision }) {
    const outcomeChartRef = React.useRef(null);
    const behaviorChartRef = React.useRef(null);
    const outcomeChartInstance = React.useRef(null);
    const behaviorChartInstance = React.useRef(null);
    
    React.useEffect(() => {
        // Outcome chart
        if (outcomeChartInstance.current) {
            outcomeChartInstance.current.destroy();
        }
        
        const ctx1 = outcomeChartRef.current.getContext('2d');
        outcomeChartInstance.current = new Chart(ctx1, {
            type: 'doughnut',
            data: {
                labels: ['Repaid', 'Defaulted'],
                datasets: [{
                    data: [decision.repaid_count, decision.default_count],
                    backgroundColor: ['#10b981', '#ef4444'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { color: '#94a3b8' } }
                }
            }
        });
        
        // Payment behavior chart
        if (behaviorChartInstance.current) {
            behaviorChartInstance.current.destroy();
        }
        
        const lateBuckets = { '0': 0, '1-15': 0, '16-30': 0, '31-60': 0, '60+': 0 };
        twins.forEach(t => {
            if (t.days_late === 0) lateBuckets['0']++;
            else if (t.days_late <= 15) lateBuckets['1-15']++;
            else if (t.days_late <= 30) lateBuckets['16-30']++;
            else if (t.days_late <= 60) lateBuckets['31-60']++;
            else lateBuckets['60+']++;
        });
        
        const ctx2 = behaviorChartRef.current.getContext('2d');
        behaviorChartInstance.current = new Chart(ctx2, {
            type: 'bar',
            data: {
                labels: Object.keys(lateBuckets),
                datasets: [{
                    label: 'Cases',
                    data: Object.values(lateBuckets),
                    backgroundColor: ['#10b981', '#22c55e', '#eab308', '#f97316', '#ef4444']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } },
                    x: { ticks: { color: '#94a3b8' }, grid: { display: false }, title: { display: true, text: 'Days Late', color: '#94a3b8' } }
                }
            }
        });
        
        return () => {
            if (outcomeChartInstance.current) outcomeChartInstance.current.destroy();
            if (behaviorChartInstance.current) behaviorChartInstance.current.destroy();
        };
    }, [twins, decision]);
    
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-slate-800 rounded-xl p-6 card-glow">
                <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <span className="w-8 h-8 bg-green-500/20 rounded-lg flex items-center justify-center text-green-400">4</span>
                    Cohort Outcome Analysis
                </h2>
                <div className="h-48">
                    <canvas ref={outcomeChartRef}></canvas>
                </div>
                <div className="mt-4 grid grid-cols-2 gap-4 text-center">
                    <div className="bg-slate-700/50 rounded-lg p-3">
                        <p className="text-2xl font-bold text-green-400">{((1 - decision.default_rate) * 100).toFixed(0)}%</p>
                        <p className="text-xs text-slate-400">Repaid Rate</p>
                    </div>
                    <div className="bg-slate-700/50 rounded-lg p-3">
                        <p className="text-2xl font-bold text-red-400">{(decision.default_rate * 100).toFixed(0)}%</p>
                        <p className="text-xs text-slate-400">Default Rate</p>
                    </div>
                </div>
            </div>
            
            <div className="bg-slate-800 rounded-xl p-6 card-glow">
                <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <span className="w-8 h-8 bg-cyan-500/20 rounded-lg flex items-center justify-center text-cyan-400">5</span>
                    Payment Behavior Distribution
                </h2>
                <div className="h-48">
                    <canvas ref={behaviorChartRef}></canvas>
                </div>
                <div className="mt-4 text-center">
                    <p className="text-sm text-slate-400">Avg Days Late in Cohort</p>
                    <p className="text-2xl font-bold text-blue-400">{decision.avg_days_late.toFixed(1)} days</p>
                </div>
            </div>
        </div>
    );
}

function ExplanationSection({ twins, decision, anomalyScore }) {
    return (
        <div className="bg-slate-800 rounded-xl p-6 card-glow">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <span className="w-8 h-8 bg-indigo-500/20 rounded-lg flex items-center justify-center text-indigo-400">6</span>
                Decision Explanation (Audit Trail)
            </h2>
            <div className="space-y-4">
                <div className="bg-slate-700/50 rounded-lg p-4">
                    <h4 className="font-semibold text-blue-400 mb-2">📋 Decision Summary</h4>
                    <p className="text-slate-300">
                        Based on analysis of <strong>{twins.length} similar historical borrowers</strong> retrieved from the Qdrant vector database:
                    </p>
                    <ul className="mt-2 space-y-1 text-slate-300">
                        <li>• <strong>{decision.repaid_count}</strong> borrowers repaid successfully ({((1 - decision.default_rate) * 100).toFixed(1)}%)</li>
                        <li>• <strong>{decision.default_count}</strong> borrowers defaulted ({(decision.default_rate * 100).toFixed(1)}%)</li>
                        <li>• Average days late in cohort: <strong>{decision.avg_days_late.toFixed(1)} days</strong></li>
                        <li>• Anomaly score: <strong>{(anomalyScore * 100).toFixed(0)}%</strong> ({anomalyScore < 0.3 ? 'typical' : anomalyScore < 0.6 ? 'somewhat unusual' : 'highly unusual'} profile)</li>
                    </ul>
                </div>
                
                <div className="bg-slate-700/50 rounded-lg p-4">
                    <h4 className="font-semibold text-purple-400 mb-2">🔍 Vector Similarity Analysis</h4>
                    <p className="text-slate-300">
                        The applicant's profile was embedded into a {VECTOR_DIMENSIONS}-dimensional vector space using the multimodal feature representation. 
                        The top {twins.length} most similar cases were retrieved using cosine similarity search in Qdrant.
                    </p>
                    <ul className="mt-2 space-y-1 text-slate-300">
                        <li>• Highest similarity match: <strong>{(twins[0].similarity * 100).toFixed(1)}%</strong> ({twins[0].id})</li>
                        <li>• This borrower had credit score {twins[0].credit_score}, income ${twins[0].income.toLocaleString()}, and {twins[0].outcome.toLowerCase()}</li>
                    </ul>
                </div>
                
                <div className="bg-slate-700/50 rounded-lg p-4">
                    <h4 className="font-semibold text-green-400 mb-2">✅ Audit Trail</h4>
                    <p className="text-slate-300 text-sm font-mono">
                        Decision timestamp: {new Date().toISOString()}<br/>
                        Model version: CreditTwin v1.0<br/>
                        Vector collection: credit_cases<br/>
                        Similarity metric: Cosine<br/>
                        k-neighbors: {twins.length}<br/>
                        Case IDs used: {twins.slice(0, 5).map(t => t.id).join(', ')}...
                    </p>
                </div>
            </div>
        </div>
    );
}

function ResultsPanel({ results, hasData }) {
    if (!hasData) {
        return (
            <div className="bg-slate-800/50 rounded-xl p-12 text-center border-2 border-dashed border-amber-500/50">
                <svg className="w-16 h-16 mx-auto text-amber-500 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/>
                </svg>
                <h3 className="text-lg font-medium text-amber-400">No Historical Data Loaded</h3>
                <p className="text-sm text-slate-400 mt-2">Please upload your Excel dataset in the "Historical Database" tab to enable credit decisions.</p>
            </div>
        );
    }
    
    if (!results) {
        return (
            <div className="bg-slate-800/50 rounded-xl p-12 text-center border-2 border-dashed border-slate-700">
                <svg className="w-16 h-16 mx-auto text-slate-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                </svg>
                <h3 className="text-lg font-medium text-slate-400">Submit an Application</h3>
                <p className="text-sm text-slate-500 mt-2">Enter borrower information and click "Find Financial Twins" to see the credit decision analysis</p>
            </div>
        );
    }
    
    const { twins, anomaly_score, flags, decision } = results;
    
    return (
        <div className="space-y-6">
            <DecisionBanner decision={decision} anomalyScore={anomaly_score} />
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <TwinsList twins={twins} />
                <AnomalyRadar twins={twins} anomalyScore={anomaly_score} flags={flags} />
            </div>
            
            <CohortCharts twins={twins} decision={decision} />
            
            <ExplanationSection twins={twins} decision={decision} anomalyScore={anomaly_score} />
        </div>
    );
}
