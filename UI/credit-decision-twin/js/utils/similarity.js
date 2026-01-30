// Similarity and decision-making functions for CreditTwin

function normalizeFeature(value, min, max) {
    return (value - min) / (max - min);
}

function createFeatureVector(applicant) {
    // Create a simplified feature vector for similarity calculation
    return [
        normalizeFeature(applicant.age, 18, 80),
        normalizeFeature(applicant.creditScore, 300, 850),
        normalizeFeature(applicant.income, 10000, 500000),
        normalizeFeature(applicant.debt, 0, 300000),
        normalizeFeature(applicant.assets, 0, 2000000),
        normalizeFeature(applicant.loanAmount, 1000, 500000),
        normalizeFeature(applicant.tenure, 6, 84),
        normalizeFeature(applicant.delinquencies, 0, 12),
        normalizeFeature(applicant.utilization, 0, 100),
        normalizeFeature(applicant.historyLength, 0, 50),
        // Categorical encodings (one-hot simplified to numeric)
        EMPLOYMENT_TYPES.indexOf(applicant.employment) / EMPLOYMENT_TYPES.length,
        SECTORS.indexOf(applicant.sector) / SECTORS.length,
        PURPOSES.indexOf(applicant.purpose) / PURPOSES.length,
        REGIONS.indexOf(applicant.region) / REGIONS.length
    ];
}

function cosineSimilarity(vecA, vecB) {
    let dotProduct = 0;
    let normA = 0;
    let normB = 0;
    
    for (let i = 0; i < vecA.length; i++) {
        dotProduct += vecA[i] * vecB[i];
        normA += vecA[i] * vecA[i];
        normB += vecB[i] * vecB[i];
    }
    
    return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
}

function findFinancialTwins(applicant, k = 50) {
    const applicantVector = createFeatureVector(applicant);
    const cases = getHistoricalCases();
    
    const similarities = cases.map(caseData => {
        const caseVector = createFeatureVector(caseData);
        const similarity = cosineSimilarity(applicantVector, caseVector);
        return { ...caseData, similarity };
    });
    
    similarities.sort((a, b) => b.similarity - a.similarity);
    return similarities.slice(0, k);
}

function calculateAnomalyScore(twins) {
    if (twins.length === 0) return 1.0;
    
    const maxSim = twins[0].similarity;
    const avgSim = twins.reduce((sum, t) => sum + t.similarity, 0) / twins.length;
    const decayRate = (twins[0].similarity - twins[Math.min(9, twins.length - 1)].similarity) / twins[0].similarity;
    
    // Anomaly is high when max similarity is low or decay is rapid
    const anomalyFromSimilarity = 1 - maxSim;
    const anomalyFromDecay = decayRate;
    const anomalyFromDensity = 1 - avgSim;
    
    return Math.min(1, (anomalyFromSimilarity * 0.4 + anomalyFromDecay * 0.3 + anomalyFromDensity * 0.3));
}

function detectAnomalyFlags(applicant) {
    const flags = [];
    
    // High income with low credit score
    if (applicant.income > 150000 && applicant.creditScore < 600) {
        flags.push({ type: 'warning', text: 'High income but low credit score - unusual combination' });
    }
    
    // High loan amount for thin file
    if (applicant.loanAmount > applicant.income * 2 && applicant.historyLength < 3) {
        flags.push({ type: 'warning', text: 'Large loan request with thin credit history' });
    }
    
    // High utilization with high assets
    if (applicant.utilization > 80 && applicant.assets > 500000) {
        flags.push({ type: 'info', text: 'High utilization despite significant assets' });
    }
    
    // Recent delinquencies with good score
    if (applicant.delinquencies > 3 && applicant.creditScore > 700) {
        flags.push({ type: 'warning', text: 'Recent delinquencies inconsistent with credit score' });
    }
    
    // Very high DTI
    const dti = applicant.debt / applicant.income;
    if (dti > 0.5) {
        flags.push({ type: 'alert', text: `High debt-to-income ratio: ${(dti * 100).toFixed(1)}%` });
    }
    
    return flags;
}

function makeDecision(twins, anomalyScore, applicant) {
    const defaultCount = twins.filter(t => t.outcome === 'DEFAULTED').length;
    const defaultRate = defaultCount / twins.length;
    
    const avgDaysLate = twins.reduce((sum, t) => sum + t.daysLate, 0) / twins.length;
    
    // Decision logic
    let decision, confidence, riskTier, reason;
    
    if (defaultRate < 0.1 && anomalyScore < 0.3) {
        decision = 'APPROVE';
        confidence = 0.85 + (1 - defaultRate) * 0.1 - anomalyScore * 0.1;
        riskTier = 'LOW';
        reason = 'Strong cohort performance and typical profile';
    } else if (defaultRate < 0.2 && anomalyScore < 0.5) {
        decision = 'CONDITIONAL';
        confidence = 0.7 + (1 - defaultRate) * 0.1 - anomalyScore * 0.1;
        riskTier = 'MEDIUM';
        reason = 'Moderate risk - additional verification recommended';
    } else if (anomalyScore > 0.6) {
        decision = 'DECLINE';
        confidence = 0.6 + anomalyScore * 0.3;
        riskTier = 'HIGH';
        reason = 'Profile significantly different from historical cases';
    } else if (defaultRate > 0.25) {
        decision = 'DECLINE';
        confidence = 0.7 + defaultRate * 0.2;
        riskTier = 'HIGH';
        reason = 'Similar borrowers have high default rates';
    } else {
        decision = 'CONDITIONAL';
        confidence = 0.65;
        riskTier = 'MEDIUM';
        reason = 'Mixed signals - manual review recommended';
    }
    
    return {
        decision,
        confidence: Math.min(0.99, confidence),
        riskTier,
        reason,
        defaultRate,
        avgDaysLate,
        repaidCount: twins.length - defaultCount,
        defaultCount
    };
}

// Process a full credit application
function processCreditApplication(applicant) {
    const twins = findFinancialTwins(applicant, 50);
    const anomalyScore = calculateAnomalyScore(twins);
    const flags = detectAnomalyFlags(applicant);
    const decision = makeDecision(twins, anomalyScore, applicant);
    
    return {
        twins,
        anomalyScore,
        flags,
        decision
    };
}
