// Architecture Tab Component - explains the CreditTwin system

function ArchitectureTab() {
    return (
        <div className="space-y-6">
            {/* Overview */}
            <div className="bg-slate-800 rounded-xl p-6 card-glow">
                <h2 className="text-xl font-bold mb-4">🏗️ CreditTwin Architecture Overview</h2>
                <p className="text-slate-300 mb-4">
                    CreditTwin is a multimodal credit decision system that combines <strong className="text-blue-400">vector similarity search</strong> 
                    with <strong className="text-orange-400">anomaly detection</strong> to provide explainable, auditable credit decisions.
                </p>
                <div className="bg-slate-900 rounded-lg p-4 font-mono text-sm overflow-x-auto">
                    <pre className="text-green-400">{`
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CreditTwin Pipeline                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌───────────┐ │
│  │  New Loan    │───▶│  Feature     │───▶│  Embedding   │───▶│  Qdrant   │ │
│  │  Application │    │  Extraction  │    │  Generation  │    │  Query    │ │
│  └──────────────┘    └──────────────┘    └──────────────┘    └─────┬─────┘ │
│                                                                     │       │
│                      ┌──────────────────────────────────────────────┘       │
│                      │                                                       │
│                      ▼                                                       │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                         QDRANT VECTOR DATABASE                        │   │
│  │  ┌────────────────────────────────────────────────────────────────┐  │   │
│  │  │  Historical Credit Cases (Embeddings + Metadata Payloads)      │  │   │
│  │  │  • Vector: Dense 768-dim embedding (cosine similarity)         │  │   │
│  │  │  • Payload: borrower_id, decision, outcome, days_late, etc.    │  │   │
│  │  └────────────────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                      │                                                       │
│          ┌───────────┴───────────┐                                          │
│          ▼                       ▼                                          │
│  ┌──────────────┐        ┌──────────────┐                                   │
│  │  Financial   │        │   Anomaly    │                                   │
│  │  Twin Match  │        │   Detection  │                                   │
│  └──────┬───────┘        └──────┬───────┘                                   │
│         │                       │                                           │
│         └───────────┬───────────┘                                           │
│                     ▼                                                       │
│           ┌──────────────────┐                                              │
│           │  Decision Logic  │                                              │
│           │  APPROVE/COND/   │                                              │
│           │  DECLINE         │                                              │
│           └────────┬─────────┘                                              │
│                    ▼                                                        │
│           ┌──────────────────┐                                              │
│           │   Explainable    │                                              │
│           │   Output +       │                                              │
│           │   Audit Trail    │                                              │
│           └──────────────────┘                                              │
└─────────────────────────────────────────────────────────────────────────────┘`}</pre>
                </div>
            </div>

            {/* Key Components */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-slate-800 rounded-xl p-6 card-glow">
                    <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                        <span className="text-2xl">🔍</span> Financial Twin Retrieval
                    </h3>
                    <p className="text-slate-300 text-sm mb-4">
                        For every new applicant, we embed the application into a high-dimensional vector space and query Qdrant for the top-k most similar historical borrowers.
                    </p>
                    <ul className="space-y-2 text-sm">
                        <li className="flex items-start gap-2">
                            <span className="text-green-400">✓</span>
                            <span>Retrieve top-k neighbors (e.g., k=50) with full payload</span>
                        </li>
                        <li className="flex items-start gap-2">
                            <span className="text-green-400">✓</span>
                            <span>Apply filters: loan type, country, product segment</span>
                        </li>
                        <li className="flex items-start gap-2">
                            <span className="text-green-400">✓</span>
                            <span>Compute empirical default rate in neighbor cohort</span>
                        </li>
                        <li className="flex items-start gap-2">
                            <span className="text-green-400">✓</span>
                            <span>Analyze distribution of days-late, recovery rates</span>
                        </li>
                    </ul>
                </div>

                <div className="bg-slate-800 rounded-xl p-6 card-glow">
                    <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                        <span className="text-2xl">📡</span> Risk Anomaly Radar
                    </h3>
                    <p className="text-slate-300 text-sm mb-4">
                        Measures how "typical" the applicant is by examining similarity distributions and density around the vector.
                    </p>
                    <ul className="space-y-2 text-sm">
                        <li className="flex items-start gap-2">
                            <span className="text-orange-400">⚠</span>
                            <span>Compare max similarity to typical database values</span>
                        </li>
                        <li className="flex items-start gap-2">
                            <span className="text-orange-400">⚠</span>
                            <span>Measure similarity decay after first neighbors</span>
                        </li>
                        <li className="flex items-start gap-2">
                            <span className="text-orange-400">⚠</span>
                            <span>Query wider radius (k=1000) for local density</span>
                        </li>
                        <li className="flex items-start gap-2">
                            <span className="text-orange-400">⚠</span>
                            <span>Flag rare/conflicting combinations as anomalies</span>
                        </li>
                    </ul>
                </div>
            </div>

            {/* Decision Logic */}
            <div className="bg-slate-800 rounded-xl p-6 card-glow">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <span className="text-2xl">⚖️</span> Decision Logic
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-4">
                        <h4 className="font-semibold text-green-400 mb-2">✅ APPROVE</h4>
                        <p className="text-sm text-slate-300">
                            Cohort default rate is <strong>LOW</strong> AND anomaly score is <strong>LOW</strong>
                        </p>
                        <p className="text-xs text-slate-400 mt-2">→ Standard terms offered</p>
                    </div>
                    <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4">
                        <h4 className="font-semibold text-yellow-400 mb-2">⚠️ CONDITIONAL</h4>
                        <p className="text-sm text-slate-300">
                            Default rate is <strong>MODERATE</strong> BUT anomaly score is <strong>LOW</strong>
                        </p>
                        <p className="text-xs text-slate-400 mt-2">→ Lower amount, higher interest, more documentation</p>
                    </div>
                    <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
                        <h4 className="font-semibold text-red-400 mb-2">❌ DECLINE</h4>
                        <p className="text-sm text-slate-300">
                            Default rate is <strong>HIGH</strong> OR anomaly score is <strong>HIGH</strong>
                        </p>
                        <p className="text-xs text-slate-400 mt-2">→ Declined or escalate to manual review</p>
                    </div>
                </div>
            </div>

            {/* Multimodal Input Signals */}
            <div className="bg-slate-800 rounded-xl p-6 card-glow">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <span className="text-2xl">📊</span> Multimodal Input Signals
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-slate-700/50 rounded-lg p-4">
                        <h4 className="font-medium text-blue-400 mb-2">Tabular Features</h4>
                        <div className="flex flex-wrap gap-1">
                            {['Age', 'Income', 'Debt', 'Assets', 'Loan Amount', 'Tenure', 'Credit Score'].map(tag => (
                                <span key={tag} className="feature-tag bg-blue-500/20 text-blue-300">{tag}</span>
                            ))}
                        </div>
                    </div>
                    <div className="bg-slate-700/50 rounded-lg p-4">
                        <h4 className="font-medium text-purple-400 mb-2">Categorical Features</h4>
                        <div className="flex flex-wrap gap-1">
                            {['Employment Type', 'Sector', 'Region', 'Loan Purpose'].map(tag => (
                                <span key={tag} className="feature-tag bg-purple-500/20 text-purple-300">{tag}</span>
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            {/* Tech Stack */}
            <div className="bg-slate-800 rounded-xl p-6 card-glow">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <span className="text-2xl">🛠️</span> Technology Stack
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-slate-700/50 rounded-lg p-4 text-center">
                        <p className="text-2xl mb-2">⚛️</p>
                        <p className="font-medium">React.js</p>
                        <p className="text-xs text-slate-400">Frontend UI</p>
                    </div>
                    <div className="bg-slate-700/50 rounded-lg p-4 text-center">
                        <p className="text-2xl mb-2">🐍</p>
                        <p className="font-medium">FastAPI</p>
                        <p className="text-xs text-slate-400">Python Backend</p>
                    </div>
                    <div className="bg-slate-700/50 rounded-lg p-4 text-center">
                        <p className="text-2xl mb-2">🔷</p>
                        <p className="font-medium">Qdrant</p>
                        <p className="text-xs text-slate-400">Vector Database</p>
                    </div>
                    <div className="bg-slate-700/50 rounded-lg p-4 text-center">
                        <p className="text-2xl mb-2">📊</p>
                        <p className="font-medium">Pandas</p>
                        <p className="text-xs text-slate-400">Data Processing</p>
                    </div>
                </div>
            </div>

            {/* Qdrant Integration */}
            <div className="bg-slate-800 rounded-xl p-6 card-glow">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <span className="text-2xl">🗄️</span> Qdrant Vector Database Integration
                </h3>
                <div className="bg-slate-900 rounded-lg p-4 font-mono text-sm mb-4 overflow-x-auto">
                    <pre className="text-blue-300">{`# Example Qdrant Point Structure
{
    "id": "loan_12345",
    "vector": [0.123, -0.456, 0.789, ...],  # 768-dim embedding
    "payload": {
        "borrower_id": "BRW_98765",
        "decision": "APPROVED",
        "outcome": "REPAID",
        "days_late": 0,
        "loan_purpose": "home",
        "credit_score": 720,
        "income": 85000,
        "loan_amount": 250000,
        "segment": "prime",
        "decision_date": "2023-06-15"
    }
}

# Similarity Search Query
qdrant.search(
    collection_name="credit_cases",
    query_vector=applicant_embedding,
    limit=50,
    query_filter={
        "must": [
            {"key": "loan_purpose", "match": {"value": "home"}},
            {"key": "decision_date", "range": {"gte": "2021-01-01"}}
        ]
    }
)`}</pre>
                </div>
                <p className="text-sm text-slate-400">
                    Qdrant's HNSW-based approximate nearest neighbor index provides fast retrieval even with 150,000+ cases. 
                    The cosine similarity metric emphasizes directional similarity in feature space.
                </p>
            </div>
        </div>
    );
}
