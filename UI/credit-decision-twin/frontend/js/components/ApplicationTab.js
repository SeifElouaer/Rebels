// Application Tab Component - combines form and results

function ApplicationForm({ onSubmit, isProcessing, hasData }) {
    const [formData, setFormData] = React.useState(DEFAULT_APPLICANT);
    
    const handleChange = (field, value) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    };
    
    const handleSubmit = (e) => {
        e.preventDefault();
        if (!hasData) {
            alert('Please upload a historical dataset first in the "Historical Database" tab.');
            return;
        }
        onSubmit(formData);
    };
    
    return (
        <div className="bg-slate-800 rounded-xl p-6 card-glow">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <span className="w-8 h-8 bg-blue-500/20 rounded-lg flex items-center justify-center text-blue-400">1</span>
                Applicant Information
            </h2>
            
            <form onSubmit={handleSubmit} className="space-y-4">
                {/* Tabular Features */}
                <div className="space-y-3">
                    <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wide">Tabular Features</h3>
                    
                    <div className="grid grid-cols-2 gap-3">
                        <div>
                            <label className="text-xs text-slate-400">Age</label>
                            <input type="number" value={formData.age} onChange={(e) => handleChange('age', parseInt(e.target.value))} min="18" max="100" className="w-full bg-slate-700 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none" />
                        </div>
                        <div>
                            <label className="text-xs text-slate-400">Credit Score</label>
                            <input type="number" value={formData.credit_score} onChange={(e) => handleChange('credit_score', parseInt(e.target.value))} min="300" max="850" className="w-full bg-slate-700 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none" />
                        </div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-3">
                        <div>
                            <label className="text-xs text-slate-400">Annual Income ($)</label>
                            <input type="number" value={formData.income} onChange={(e) => handleChange('income', parseFloat(e.target.value))} min="10000" max="10000000" step="1000" className="w-full bg-slate-700 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none" />
                        </div>
                        <div>
                            <label className="text-xs text-slate-400">Total Debt ($)</label>
                            <input type="number" value={formData.debt} onChange={(e) => handleChange('debt', parseFloat(e.target.value))} min="0" max="10000000" step="1000" className="w-full bg-slate-700 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none" />
                        </div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-3">
                        <div>
                            <label className="text-xs text-slate-400">Loan Amount ($)</label>
                            <input type="number" value={formData.loan_amount} onChange={(e) => handleChange('loan_amount', parseFloat(e.target.value))} min="1000" max="10000000" step="1000" className="w-full bg-slate-700 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none" />
                        </div>
                        <div>
                            <label className="text-xs text-slate-400">Loan Term (months)</label>
                            <input type="number" value={formData.tenure} onChange={(e) => handleChange('tenure', parseInt(e.target.value))} min="6" max="360" className="w-full bg-slate-700 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none" />
                        </div>
                    </div>
                    
                    <div>
                        <label className="text-xs text-slate-400">Total Assets ($)</label>
                        <input type="number" value={formData.assets} onChange={(e) => handleChange('assets', parseFloat(e.target.value))} min="0" max="100000000" step="5000" className="w-full bg-slate-700 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none" />
                    </div>
                </div>
                
                {/* Categorical Features */}
                <div className="space-y-3 pt-2 border-t border-slate-700">
                    <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wide">Categorical Features</h3>
                    
                    <div>
                        <label className="text-xs text-slate-400">Employment Type</label>
                        <select value={formData.employment} onChange={(e) => handleChange('employment', e.target.value)} className="w-full bg-slate-700 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                            <option value="full-time">Full-Time Employee</option>
                            <option value="part-time">Part-Time Employee</option>
                            <option value="self-employed">Self-Employed</option>
                            <option value="contractor">Contractor</option>
                            <option value="retired">Retired</option>
                        </select>
                    </div>
                    
                    <div>
                        <label className="text-xs text-slate-400">Industry Sector</label>
                        <select value={formData.sector} onChange={(e) => handleChange('sector', e.target.value)} className="w-full bg-slate-700 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                            <option value="technology">Technology</option>
                            <option value="healthcare">Healthcare</option>
                            <option value="finance">Finance</option>
                            <option value="retail">Retail</option>
                            <option value="manufacturing">Manufacturing</option>
                            <option value="education">Education</option>
                            <option value="government">Government</option>
                            <option value="other">Other</option>
                        </select>
                    </div>
                    
                    <div>
                        <label className="text-xs text-slate-400">Loan Purpose</label>
                        <select value={formData.purpose} onChange={(e) => handleChange('purpose', e.target.value)} className="w-full bg-slate-700 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                            <option value="home">Home Purchase</option>
                            <option value="auto">Auto Loan</option>
                            <option value="personal">Personal Loan</option>
                            <option value="business">Business Loan</option>
                            <option value="education">Education</option>
                            <option value="debt-consolidation">Debt Consolidation</option>
                        </select>
                    </div>
                    
                    <div>
                        <label className="text-xs text-slate-400">Region</label>
                        <select value={formData.region} onChange={(e) => handleChange('region', e.target.value)} className="w-full bg-slate-700 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                            <option value="northeast">Northeast</option>
                            <option value="southeast">Southeast</option>
                            <option value="midwest">Midwest</option>
                            <option value="southwest">Southwest</option>
                            <option value="west">West</option>
                        </select>
                    </div>
                </div>
                
                <button 
                    type="submit" 
                    disabled={isProcessing || !hasData} 
                    className="w-full bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 disabled:from-slate-600 disabled:to-slate-600 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-lg transition-all flex items-center justify-center gap-2"
                >
                    {isProcessing ? (
                        <>
                            <svg className="spinner w-5 h-5" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            Searching Qdrant...
                        </>
                    ) : !hasData ? (
                        <>
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
                            </svg>
                            Upload Dataset First
                        </>
                    ) : (
                        <>
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
                            </svg>
                            Find Financial Twins
                        </>
                    )}
                </button>
                
                {!hasData && (
                    <p className="text-xs text-center text-amber-400">
                        ⚠️ Please go to "Historical Database" tab and upload your credit dataset first.
                    </p>
                )}
            </form>
        </div>
    );
}

function ApplicationTab() {
    const { applicationResults, isProcessing, processApplication, dataSource } = useAppContext();
    
    const hasData = dataSource.count > 0;
    
    const handleSubmit = async (formData) => {
        try {
            await processApplication(formData);
        } catch (error) {
            console.error('Application processing failed:', error);
        }
    };
    
    return (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Form Column */}
            <div className="lg:col-span-1">
                <ApplicationForm onSubmit={handleSubmit} isProcessing={isProcessing} hasData={hasData} />
            </div>
            
            {/* Results Column */}
            <div className="lg:col-span-2">
                <ResultsPanel results={applicationResults} hasData={hasData} />
            </div>
        </div>
    );
}
