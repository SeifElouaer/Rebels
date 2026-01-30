// Synthetic data generation for CreditTwin

function generateHistoricalCase(id) {
    const creditScore = Math.floor(Math.random() * 400) + 450; // 450-850
    const income = Math.floor(Math.random() * 180000) + 20000; // 20k-200k
    const age = Math.floor(Math.random() * 50) + 22; // 22-72
    const loanAmount = Math.floor(Math.random() * income * 2) + 5000;
    const debt = Math.floor(Math.random() * income * 0.5);
    const assets = Math.floor(Math.random() * income * 3);
    const tenure = [12, 24, 36, 48, 60, 72][Math.floor(Math.random() * 6)];
    const delinquencies = creditScore > 700 ? Math.floor(Math.random() * 2) : Math.floor(Math.random() * 5);
    const utilization = Math.floor(Math.random() * 80) + 5;
    const historyLength = Math.floor(Math.random() * 20) + 1;
    
    // Calculate risk factors
    const dti = debt / income;
    const lti = loanAmount / income;
    
    // Determine outcome based on risk factors
    let defaultProb = 0.1; // base rate
    if (creditScore < 600) defaultProb += 0.25;
    else if (creditScore < 680) defaultProb += 0.1;
    if (dti > 0.4) defaultProb += 0.15;
    if (lti > 1.5) defaultProb += 0.1;
    if (delinquencies > 2) defaultProb += 0.2;
    if (utilization > 70) defaultProb += 0.1;
    
    const defaulted = Math.random() < defaultProb;
    const daysLate = defaulted ? Math.floor(Math.random() * 180) + 30 : (Math.random() < 0.2 ? Math.floor(Math.random() * 30) : 0);
    
    return {
        id: `LOAN_${String(id).padStart(5, '0')}`,
        borrowerId: `BRW_${String(Math.floor(Math.random() * 100000)).padStart(5, '0')}`,
        age,
        creditScore,
        income,
        debt,
        assets,
        loanAmount,
        tenure,
        employment: EMPLOYMENT_TYPES[Math.floor(Math.random() * EMPLOYMENT_TYPES.length)],
        sector: SECTORS[Math.floor(Math.random() * SECTORS.length)],
        purpose: PURPOSES[Math.floor(Math.random() * PURPOSES.length)],
        region: REGIONS[Math.floor(Math.random() * REGIONS.length)],
        delinquencies,
        utilization,
        historyLength,
        decision: defaulted && Math.random() < 0.3 ? 'DECLINED' : 'APPROVED',
        outcome: defaulted ? 'DEFAULTED' : 'REPAID',
        daysLate
    };
}

function generateSyntheticData(count = 1000) {
    const cases = [];
    for (let i = 1; i <= count; i++) {
        cases.push(generateHistoricalCase(i));
    }
    return cases;
}

// Initialize global historical cases
let historicalCases = generateSyntheticData(1000);

function getHistoricalCases() {
    return historicalCases;
}

function setHistoricalCases(cases) {
    historicalCases = cases;
}

function resetHistoricalCases() {
    historicalCases = generateSyntheticData(1000);
    return historicalCases;
}
