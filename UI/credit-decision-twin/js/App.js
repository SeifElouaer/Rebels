// Main App Component

function TabButton({ id, label, isActive, onClick }) {
    return (
        <button 
            onClick={() => onClick(id)}
            className={`tab-btn px-4 py-2 rounded-lg font-medium ${isActive ? 'bg-blue-600 text-white' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'}`}
        >
            {label}
        </button>
    );
}

function Footer() {
    return (
        <footer className="border-t border-slate-800 mt-12 py-6">
            <div className="max-w-7xl mx-auto px-4 text-center text-slate-500 text-sm">
                <p>CreditTwin - Hackathon 2024 | Multimodal Similarity-Driven Risk & Anomaly Detection</p>
                <p className="mt-1">Powered by Qdrant Vector Database</p>
            </div>
        </footer>
    );
}

function App() {
    const { activeTab, setActiveTab } = useAppContext();
    
    const tabs = [
        { id: 'application', label: '📝 New Application' },
        { id: 'database', label: '🗃️ Historical Database' },
        { id: 'architecture', label: '🏗️ Architecture' }
    ];
    
    return (
        <div className="min-h-screen flex flex-col">
            <Header />
            
            <main className="max-w-7xl mx-auto px-4 py-6 flex-grow w-full">
                {/* Tab Navigation */}
                <div className="flex gap-2 mb-6 flex-wrap">
                    {tabs.map(tab => (
                        <TabButton 
                            key={tab.id}
                            id={tab.id}
                            label={tab.label}
                            isActive={activeTab === tab.id}
                            onClick={setActiveTab}
                        />
                    ))}
                </div>
                
                {/* Tab Panels */}
                <div className="tab-panel">
                    {activeTab === 'application' && <ApplicationTab />}
                    {activeTab === 'database' && <DatabaseTab />}
                    {activeTab === 'architecture' && <ArchitectureTab />}
                </div>
            </main>
            
            <Footer />
        </div>
    );
}

// Render the app
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
    <AppProvider>
        <App />
    </AppProvider>
);

console.log('CreditTwin React App initialized with', getHistoricalCases().length, 'historical cases');
