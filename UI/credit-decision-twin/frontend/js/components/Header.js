// Header component

function Header() {
    const { dataSource, apiStatus } = useAppContext();
    
    const isConnected = apiStatus.api_status === 'connected';
    
    return (
        <header className="gradient-bg border-b border-slate-700 sticky top-0 z-50">
            <div className="max-w-7xl mx-auto px-4 py-4">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center">
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
                            </svg>
                        </div>
                        <div>
                            <h1 className="text-xl font-bold">CreditTwin</h1>
                            <p className="text-xs text-slate-400">Multimodal Similarity-Driven Risk & Anomaly Detection</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-4">
                        <div className="text-right">
                            <p className="text-xs text-slate-400">Historical Cases</p>
                            <p className="text-lg font-bold text-blue-400">
                                {dataSource.count > 0 ? dataSource.count.toLocaleString() : '—'}
                            </p>
                        </div>
                        <div className="text-right">
                            <p className="text-xs text-slate-400">Backend Status</p>
                            <p className={`text-sm font-medium flex items-center gap-1 ${isConnected ? 'text-green-400' : 'text-red-400'}`}>
                                <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400 pulse-animation' : 'bg-red-400'}`}></span>
                                {isConnected ? 'Connected' : 'Disconnected'}
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </header>
    );
}
