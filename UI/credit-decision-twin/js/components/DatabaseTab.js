// Database Tab Component - historical data view and file upload

function FileUpload() {
    const { fileHeaders, uploadStatus, handleFileUpload, importDataFromFile, resetToSynthetic, dataSource, setUploadStatus } = useAppContext();
    const [mappings, setMappings] = React.useState({});
    const [previewData, setPreviewData] = React.useState([]);
    const [isDragging, setIsDragging] = React.useState(false);
    const fileInputRef = React.useRef(null);
    
    const mappingFields = [
        { id: 'age', label: 'Age *', required: true },
        { id: 'creditScore', label: 'Credit Score *', required: true },
        { id: 'income', label: 'Income *', required: true },
        { id: 'loanAmount', label: 'Loan Amount *', required: true },
        { id: 'debt', label: 'Debt', required: false },
        { id: 'assets', label: 'Assets', required: false },
        { id: 'tenure', label: 'Loan Term/Tenure', required: false },
        { id: 'delinquencies', label: 'Delinquencies', required: false },
        { id: 'utilization', label: 'Utilization (%)', required: false },
        { id: 'historyLength', label: 'History Length (years)', required: false },
        { id: 'employment', label: 'Employment Type', required: false },
        { id: 'sector', label: 'Sector/Industry', required: false },
        { id: 'purpose', label: 'Loan Purpose', required: false },
        { id: 'region', label: 'Region', required: false },
        { id: 'outcome', label: 'Outcome (REPAID/DEFAULTED) *', required: true },
        { id: 'daysLate', label: 'Days Late', required: false }
    ];
    
    React.useEffect(() => {
        if (fileHeaders.length > 0) {
            const autoMappings = autoMapColumns(fileHeaders);
            setMappings(autoMappings);
        }
    }, [fileHeaders]);
    
    const handleDragOver = (e) => {
        e.preventDefault();
        setIsDragging(true);
    };
    
    const handleDragLeave = (e) => {
        e.preventDefault();
        setIsDragging(false);
    };
    
    const handleDrop = async (e) => {
        e.preventDefault();
        setIsDragging(false);
        const file = e.dataTransfer.files[0];
        if (file) {
            try {
                const result = await handleFileUpload(file);
                setPreviewData(result.data.slice(0, 5));
            } catch (err) {
                console.error(err);
            }
        }
    };
    
    const handleFileChange = async (e) => {
        const file = e.target.files[0];
        if (file) {
            try {
                const result = await handleFileUpload(file);
                setPreviewData(result.data.slice(0, 5));
            } catch (err) {
                console.error(err);
            }
        }
    };
    
    const handleMappingChange = (field, value) => {
        setMappings(prev => ({ ...prev, [field]: value }));
    };
    
    const handleImport = () => {
        const success = importDataFromFile(mappings);
        if (success) {
            setPreviewData([]);
        }
    };
    
    const handleReset = () => {
        resetToSynthetic();
        setMappings({});
        setPreviewData([]);
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };
    
    const handleDownloadTemplate = () => {
        const csvContent = generateCSVTemplate();
        downloadFile(csvContent, 'credit_twin_template.csv');
    };
    
    return (
        <div className="bg-slate-800 rounded-xl p-6 card-glow mb-6">
            <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
                <h3 className="text-lg font-semibold flex items-center gap-2">
                    <span className="text-2xl">📤</span> Upload Historical Credit Dataset (Excel / CSV)
                </h3>
                <div className="flex items-center gap-2">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${dataSource.type === 'custom' ? 'bg-green-500/20 text-green-400' : 'bg-purple-500/20 text-purple-400'}`}>
                        Using: {dataSource.label}
                    </span>
                    <button onClick={handleReset} className="px-3 py-1 bg-slate-700 hover:bg-slate-600 rounded-lg text-sm">
                        🔄 Reset to Synthetic
                    </button>
                </div>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Drop Zone */}
                <div>
                    <div 
                        className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors cursor-pointer ${isDragging ? 'border-blue-500 bg-blue-500/10' : 'border-slate-600 hover:border-blue-500'}`}
                        onDragOver={handleDragOver}
                        onDragLeave={handleDragLeave}
                        onDrop={handleDrop}
                        onClick={() => fileInputRef.current?.click()}
                    >
                        <input 
                            type="file" 
                            ref={fileInputRef}
                            onChange={handleFileChange}
                            accept=".xlsx,.xls,.csv" 
                            className="hidden" 
                        />
                        <svg className="w-12 h-12 mx-auto text-slate-500 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
                        </svg>
                        <p className="text-slate-300 font-medium mb-1">Drop your Excel or CSV file here</p>
                        <p className="text-slate-500 text-sm mb-3">Supports .xlsx, .xls, and .csv formats</p>
                        <button 
                            onClick={(e) => { e.stopPropagation(); fileInputRef.current?.click(); }}
                            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm font-medium"
                        >
                            📂 Select Excel/CSV File
                        </button>
                        <button 
                            onClick={(e) => { e.stopPropagation(); handleDownloadTemplate(); }}
                            className="mt-2 ml-2 px-4 py-2 bg-slate-600 hover:bg-slate-500 rounded-lg text-xs font-medium"
                        >
                            📥 Download Template
                        </button>
                    </div>
                    
                    {uploadStatus && (
                        <div className={`mt-4 p-4 rounded-lg ${uploadStatus.type === 'success' ? 'bg-green-500/20 text-green-400' : uploadStatus.type === 'error' ? 'bg-red-500/20 text-red-400' : 'bg-blue-500/20 text-blue-400'}`}>
                            <div className="flex items-center gap-2">
                                <span>{uploadStatus.type === 'success' ? '✅' : uploadStatus.type === 'error' ? '❌' : 'ℹ️'}</span>
                                <span>{uploadStatus.message}</span>
                            </div>
                        </div>
                    )}
                </div>
                
                {/* Column Mapping */}
                <div>
                    <h4 className="font-medium text-slate-300 mb-3">📋 Column Mapping</h4>
                    <p className="text-sm text-slate-500 mb-4">Map your file columns to the required fields. Leave empty for optional fields.</p>
                    
                    <div className="space-y-3 max-h-64 overflow-y-auto scrollbar-thin pr-2">
                        {mappingFields.map((field, idx) => (
                            idx % 2 === 0 && (
                                <div key={field.id} className="grid grid-cols-2 gap-2">
                                    {[mappingFields[idx], mappingFields[idx + 1]].filter(Boolean).map(f => (
                                        <div key={f.id}>
                                            <label className="text-xs text-slate-400">{f.label}</label>
                                            <select 
                                                value={mappings[f.id] || ''} 
                                                onChange={(e) => handleMappingChange(f.id, e.target.value)}
                                                className="w-full bg-slate-700 rounded px-2 py-1.5 text-sm"
                                            >
                                                <option value="">-- Select Column --</option>
                                                {fileHeaders.map(header => (
                                                    <option key={header} value={header}>{header}</option>
                                                ))}
                                            </select>
                                        </div>
                                    ))}
                                </div>
                            )
                        ))}
                    </div>
                    
                    <button 
                        onClick={handleImport}
                        disabled={fileHeaders.length === 0}
                        className="mt-4 w-full px-4 py-2 bg-green-600 hover:bg-green-500 disabled:bg-slate-600 disabled:cursor-not-allowed rounded-lg text-sm font-medium flex items-center justify-center gap-2"
                    >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/>
                        </svg>
                        Import Dataset to Qdrant
                    </button>
                </div>
            </div>
            
            {/* Preview */}
            {previewData.length > 0 && fileHeaders.length > 0 && (
                <div className="mt-6">
                    <h4 className="font-medium text-slate-300 mb-3">👁️ Data Preview (First 5 Rows)</h4>
                    <div className="overflow-x-auto bg-slate-900 rounded-lg">
                        <table className="w-full text-xs">
                            <thead className="text-slate-400 border-b border-slate-700">
                                <tr>
                                    {fileHeaders.map(h => <th key={h} className="px-3 py-2 text-left">{h}</th>)}
                                </tr>
                            </thead>
                            <tbody className="text-slate-300 divide-y divide-slate-800">
                                {previewData.map((row, i) => (
                                    <tr key={i}>
                                        {fileHeaders.map(h => <td key={h} className="px-3 py-2">{row[h] !== undefined ? String(row[h]) : '-'}</td>)}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
}

function StatsCards() {
    const { getStats } = useAppContext();
    const stats = getStats();
    
    return (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-6">
            <div className="bg-slate-800 rounded-xl p-6 card-glow">
                <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-blue-500/20 rounded-xl flex items-center justify-center">
                        <svg className="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
                        </svg>
                    </div>
                    <div>
                        <p className="text-2xl font-bold">{stats.total.toLocaleString()}</p>
                        <p className="text-sm text-slate-400">Total Cases</p>
                    </div>
                </div>
            </div>
            <div className="bg-slate-800 rounded-xl p-6 card-glow">
                <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-green-500/20 rounded-xl flex items-center justify-center">
                        <svg className="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                        </svg>
                    </div>
                    <div>
                        <p className="text-2xl font-bold">{stats.repaid.toLocaleString()}</p>
                        <p className="text-sm text-slate-400">Repaid</p>
                    </div>
                </div>
            </div>
            <div className="bg-slate-800 rounded-xl p-6 card-glow">
                <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-red-500/20 rounded-xl flex items-center justify-center">
                        <svg className="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                        </svg>
                    </div>
                    <div>
                        <p className="text-2xl font-bold">{stats.defaulted.toLocaleString()}</p>
                        <p className="text-sm text-slate-400">Defaulted</p>
                    </div>
                </div>
            </div>
            <div className="bg-slate-800 rounded-xl p-6 card-glow">
                <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-purple-500/20 rounded-xl flex items-center justify-center">
                        <svg className="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4"/>
                        </svg>
                    </div>
                    <div>
                        <p className="text-2xl font-bold">{VECTOR_DIMENSIONS}</p>
                        <p className="text-sm text-slate-400">Vector Dims</p>
                    </div>
                </div>
            </div>
        </div>
    );
}

function DatabaseCharts() {
    const { getStats } = useAppContext();
    const stats = getStats();
    const outcomeChartRef = React.useRef(null);
    const purposeChartRef = React.useRef(null);
    const chartInstances = React.useRef({ outcome: null, purpose: null });
    
    React.useEffect(() => {
        // Outcome chart
        if (chartInstances.current.outcome) {
            chartInstances.current.outcome.destroy();
        }
        
        const ctx1 = outcomeChartRef.current.getContext('2d');
        chartInstances.current.outcome = new Chart(ctx1, {
            type: 'doughnut',
            data: {
                labels: ['Repaid', 'Defaulted'],
                datasets: [{
                    data: [stats.repaid, stats.defaulted],
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
        
        // Purpose chart
        if (chartInstances.current.purpose) {
            chartInstances.current.purpose.destroy();
        }
        
        const ctx2 = purposeChartRef.current.getContext('2d');
        chartInstances.current.purpose = new Chart(ctx2, {
            type: 'bar',
            data: {
                labels: PURPOSES.map(p => p.charAt(0).toUpperCase() + p.slice(1).replace('-', ' ')),
                datasets: [{
                    label: 'Loan Count',
                    data: PURPOSES.map(p => stats.purposeCounts[p] || 0),
                    backgroundColor: '#3b82f6'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } },
                    x: { ticks: { color: '#94a3b8' }, grid: { display: false } }
                }
            }
        });
        
        return () => {
            if (chartInstances.current.outcome) chartInstances.current.outcome.destroy();
            if (chartInstances.current.purpose) chartInstances.current.purpose.destroy();
        };
    }, [stats]);
    
    return (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <div className="bg-slate-800 rounded-xl p-6 card-glow">
                <h3 className="text-lg font-semibold mb-4">Outcome Distribution</h3>
                <div className="h-64">
                    <canvas ref={outcomeChartRef}></canvas>
                </div>
            </div>
            <div className="bg-slate-800 rounded-xl p-6 card-glow">
                <h3 className="text-lg font-semibold mb-4">Loan Purpose Breakdown</h3>
                <div className="h-64">
                    <canvas ref={purposeChartRef}></canvas>
                </div>
            </div>
        </div>
    );
}

function SampleDataTable() {
    const [sampleData, setSampleData] = React.useState([]);
    
    const refreshSample = () => {
        const cases = getHistoricalCases();
        const shuffled = [...cases].sort(() => Math.random() - 0.5);
        setSampleData(shuffled.slice(0, 20));
    };
    
    const handleExport = () => {
        const csvContent = exportCurrentData();
        downloadFile(csvContent, `credit_twin_data_${new Date().toISOString().split('T')[0]}.csv`);
    };
    
    React.useEffect(() => {
        refreshSample();
    }, []);
    
    return (
        <div className="bg-slate-800 rounded-xl p-6 card-glow">
            <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
                <h3 className="text-lg font-semibold">Sample Historical Cases</h3>
                <div className="flex gap-2">
                    <button onClick={handleExport} className="px-3 py-1 bg-green-600 hover:bg-green-500 rounded-lg text-sm">
                        📥 Export All Data
                    </button>
                    <button onClick={refreshSample} className="px-3 py-1 bg-slate-700 hover:bg-slate-600 rounded-lg text-sm">
                        🔄 Refresh Sample
                    </button>
                </div>
            </div>
            <div className="overflow-x-auto">
                <table className="w-full text-sm">
                    <thead>
                        <tr className="text-left text-slate-400 border-b border-slate-700">
                            <th className="pb-3 pr-4">ID</th>
                            <th className="pb-3 pr-4">Age</th>
                            <th className="pb-3 pr-4">Credit Score</th>
                            <th className="pb-3 pr-4">Income</th>
                            <th className="pb-3 pr-4">Loan Amount</th>
                            <th className="pb-3 pr-4">Purpose</th>
                            <th className="pb-3 pr-4">Decision</th>
                            <th className="pb-3 pr-4">Outcome</th>
                            <th className="pb-3">Days Late</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-700">
                        {sampleData.map(c => (
                            <tr key={c.id} className="text-slate-300">
                                <td className="py-2 pr-4 font-mono text-xs">{c.id}</td>
                                <td className="py-2 pr-4">{c.age}</td>
                                <td className="py-2 pr-4">{c.creditScore}</td>
                                <td className="py-2 pr-4">${c.income.toLocaleString()}</td>
                                <td className="py-2 pr-4">${c.loanAmount.toLocaleString()}</td>
                                <td className="py-2 pr-4 capitalize">{c.purpose.replace('-', ' ')}</td>
                                <td className="py-2 pr-4">
                                    <span className={`px-2 py-1 rounded text-xs ${c.decision === 'APPROVED' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>{c.decision}</span>
                                </td>
                                <td className="py-2 pr-4">
                                    <span className={`px-2 py-1 rounded text-xs ${c.outcome === 'REPAID' ? 'bg-blue-500/20 text-blue-400' : 'bg-orange-500/20 text-orange-400'}`}>{c.outcome}</span>
                                </td>
                                <td className="py-2">{c.daysLate}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

function DatabaseTab() {
    return (
        <div>
            <FileUpload />
            <StatsCards />
            <DatabaseCharts />
            <SampleDataTable />
        </div>
    );
}
