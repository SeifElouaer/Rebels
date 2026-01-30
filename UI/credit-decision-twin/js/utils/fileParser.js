// File parsing utilities for Excel and CSV files

function parseCSVLine(line) {
    const result = [];
    let current = '';
    let inQuotes = false;
    
    for (let i = 0; i < line.length; i++) {
        const char = line[i];
        if (char === '"') {
            inQuotes = !inQuotes;
        } else if (char === ',' && !inQuotes) {
            result.push(current.trim());
            current = '';
        } else {
            current += char;
        }
    }
    result.push(current.trim());
    return result;
}

function parseCSV(text) {
    const lines = text.trim().split('\n');
    if (lines.length < 2) {
        throw new Error('CSV file must have at least a header row and one data row.');
    }
    
    // Parse header
    const headers = parseCSVLine(lines[0]);
    
    // Parse data rows
    const data = [];
    for (let i = 1; i < lines.length; i++) {
        if (lines[i].trim()) {
            const values = parseCSVLine(lines[i]);
            const row = {};
            headers.forEach((header, idx) => {
                row[header] = values[idx] || '';
            });
            data.push(row);
        }
    }
    
    return { headers, data };
}

function parseExcel(arrayBuffer) {
    const data = new Uint8Array(arrayBuffer);
    const workbook = XLSX.read(data, { type: 'array' });
    
    // Get first sheet
    const firstSheetName = workbook.SheetNames[0];
    const worksheet = workbook.Sheets[firstSheetName];
    
    // Convert to JSON
    const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 });
    
    if (jsonData.length < 2) {
        throw new Error('Excel file must have at least a header row and one data row.');
    }
    
    // First row is headers
    const headers = jsonData[0].map(h => String(h || '').trim());
    
    // Rest are data rows
    const rows = [];
    for (let i = 1; i < jsonData.length; i++) {
        const rowData = jsonData[i];
        if (rowData && rowData.some(cell => cell !== null && cell !== undefined && cell !== '')) {
            const row = {};
            headers.forEach((header, idx) => {
                row[header] = rowData[idx] !== undefined ? rowData[idx] : '';
            });
            rows.push(row);
        }
    }
    
    return { 
        headers, 
        data: rows, 
        sheetName: firstSheetName,
        sheetCount: workbook.SheetNames.length 
    };
}

function mapCategorical(value, validOptions) {
    if (!value) return validOptions[validOptions.length - 1]; // default to 'other' or last option
    const lowerVal = value.toString().toLowerCase().replace(/[^a-z]/g, '');
    const match = validOptions.find(opt => lowerVal.includes(opt.replace('-', '')));
    return match || validOptions[validOptions.length - 1];
}

function convertToHistoricalCase(row, mappings, idx) {
    const age = parseInt(row[mappings.age]) || 35;
    const creditScore = parseInt(row[mappings.creditScore]) || 650;
    const income = parseFloat(row[mappings.income]) || 50000;
    const loanAmount = parseFloat(row[mappings.loanAmount]) || 10000;
    
    // Parse outcome
    let outcome = 'REPAID';
    const outcomeVal = (row[mappings.outcome] || '').toString().toLowerCase();
    if (outcomeVal.includes('default') || outcomeVal.includes('charged') || outcomeVal === '1' || outcomeVal === 'true' || outcomeVal.includes('late')) {
        outcome = 'DEFAULTED';
    }
    
    return {
        id: `IMPORT_${String(idx + 1).padStart(5, '0')}`,
        borrowerId: `BRW_${String(idx + 1).padStart(5, '0')}`,
        age: Math.min(80, Math.max(18, age)),
        creditScore: Math.min(850, Math.max(300, creditScore)),
        income: Math.max(0, income),
        debt: mappings.debt ? parseFloat(row[mappings.debt]) || 0 : income * 0.2,
        assets: mappings.assets ? parseFloat(row[mappings.assets]) || 0 : income * 1.5,
        loanAmount: Math.max(0, loanAmount),
        tenure: mappings.tenure ? parseInt(row[mappings.tenure]) || 36 : 36,
        employment: mappings.employment ? mapCategorical(row[mappings.employment], EMPLOYMENT_TYPES) : 'full-time',
        sector: mappings.sector ? mapCategorical(row[mappings.sector], SECTORS) : 'other',
        purpose: mappings.purpose ? mapCategorical(row[mappings.purpose], PURPOSES) : 'personal',
        region: mappings.region ? mapCategorical(row[mappings.region], REGIONS) : 'northeast',
        delinquencies: mappings.delinquencies ? parseInt(row[mappings.delinquencies]) || 0 : 0,
        utilization: mappings.utilization ? parseFloat(row[mappings.utilization]) || 30 : 30,
        historyLength: mappings.historyLength ? parseFloat(row[mappings.historyLength]) || 5 : 5,
        decision: outcome === 'DEFAULTED' ? 'DECLINED' : 'APPROVED',
        outcome: outcome,
        daysLate: mappings.daysLate ? parseInt(row[mappings.daysLate]) || 0 : (outcome === 'DEFAULTED' ? 60 : 0)
    };
}

function importDataset(uploadedData, mappings) {
    const importedCases = [];
    let skippedRows = 0;
    
    uploadedData.forEach((row, idx) => {
        try {
            const caseData = convertToHistoricalCase(row, mappings, idx);
            importedCases.push(caseData);
        } catch (e) {
            skippedRows++;
        }
    });
    
    return { importedCases, skippedRows };
}

function autoMapColumns(headers) {
    const mappings = {};
    
    Object.keys(AUTO_MAP_PATTERNS).forEach(field => {
        const patterns = AUTO_MAP_PATTERNS[field];
        for (const pattern of patterns) {
            const match = headers.find(h => h.toLowerCase().includes(pattern.toLowerCase()));
            if (match) {
                mappings[field] = match;
                break;
            }
        }
    });
    
    return mappings;
}

function generateCSVTemplate() {
    const headers = ['age', 'credit_score', 'income', 'loan_amount', 'debt', 'assets', 'tenure', 'delinquencies', 'utilization', 'history_length', 'employment', 'sector', 'purpose', 'region', 'outcome', 'days_late'];
    
    // Create sample rows from synthetic data
    const cases = getHistoricalCases();
    const sampleRows = cases.slice(0, 10).map(c => [
        c.age, c.creditScore, c.income, c.loanAmount, c.debt, c.assets, c.tenure,
        c.delinquencies, c.utilization, c.historyLength, c.employment, c.sector,
        c.purpose, c.region, c.outcome, c.daysLate
    ]);
    
    return [
        headers.join(','),
        ...sampleRows.map(row => row.join(','))
    ].join('\n');
}

function exportCurrentData() {
    const cases = getHistoricalCases();
    const headers = ['id', 'age', 'credit_score', 'income', 'loan_amount', 'debt', 'assets', 'tenure', 'delinquencies', 'utilization', 'history_length', 'employment', 'sector', 'purpose', 'region', 'decision', 'outcome', 'days_late'];
    
    const rows = cases.map(c => [
        c.id, c.age, c.creditScore, c.income, c.loanAmount, c.debt, c.assets, c.tenure,
        c.delinquencies, c.utilization, c.historyLength, c.employment, c.sector,
        c.purpose, c.region, c.decision, c.outcome, c.daysLate
    ]);
    
    return [
        headers.join(','),
        ...rows.map(row => row.join(','))
    ].join('\n');
}

function downloadFile(content, filename, type = 'text/csv;charset=utf-8;') {
    const blob = new Blob([content], { type });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
    URL.revokeObjectURL(link.href);
}
