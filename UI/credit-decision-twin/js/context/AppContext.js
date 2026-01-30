// React Context for global state management

const { createContext, useContext, useState, useCallback } = React;

// Create the context
const AppContext = createContext(null);

// Custom hook to use the context
function useAppContext() {
    const context = useContext(AppContext);
    if (!context) {
        throw new Error('useAppContext must be used within an AppProvider');
    }
    return context;
}

// Provider component
function AppProvider({ children }) {
    // Active tab state
    const [activeTab, setActiveTab] = useState('application');
    
    // Data source state
    const [dataSource, setDataSource] = useState({
        type: 'synthetic',
        count: 1000,
        label: 'Synthetic Data (1,000 cases)'
    });
    
    // Application results state
    const [applicationResults, setApplicationResults] = useState(null);
    
    // Loading state
    const [isProcessing, setIsProcessing] = useState(false);
    
    // Upload state
    const [uploadedData, setUploadedData] = useState(null);
    const [fileHeaders, setFileHeaders] = useState([]);
    const [uploadStatus, setUploadStatus] = useState(null);
    
    // Get current case count
    const getCaseCount = useCallback(() => {
        return getHistoricalCases().length;
    }, []);
    
    // Get database statistics
    const getStats = useCallback(() => {
        const cases = getHistoricalCases();
        const repaidCount = cases.filter(c => c.outcome === 'REPAID').length;
        const defaultedCount = cases.filter(c => c.outcome === 'DEFAULTED').length;
        
        const purposeCounts = {};
        PURPOSES.forEach(p => purposeCounts[p] = 0);
        cases.forEach(c => purposeCounts[c.purpose]++);
        
        return {
            total: cases.length,
            repaid: repaidCount,
            defaulted: defaultedCount,
            purposeCounts
        };
    }, []);
    
    // Process a credit application
    const processApplication = useCallback((applicant) => {
        setIsProcessing(true);
        
        // Simulate processing delay
        return new Promise((resolve) => {
            setTimeout(() => {
                const results = processCreditApplication(applicant);
                setApplicationResults(results);
                setIsProcessing(false);
                resolve(results);
            }, 1500);
        });
    }, []);
    
    // Import dataset from uploaded file
    const importDataFromFile = useCallback((mappings) => {
        if (!uploadedData || uploadedData.length === 0) {
            setUploadStatus({ type: 'error', message: 'No data to import. Please upload a file first.' });
            return false;
        }
        
        // Validate required fields
        if (!mappings.age || !mappings.creditScore || !mappings.income || !mappings.loanAmount || !mappings.outcome) {
            setUploadStatus({ type: 'error', message: 'Please map all required fields: Age, Credit Score, Income, Loan Amount, and Outcome.' });
            return false;
        }
        
        const { importedCases, skippedRows } = importDataset(uploadedData, mappings);
        
        if (importedCases.length === 0) {
            setUploadStatus({ type: 'error', message: 'Could not import any valid rows. Please check your column mappings.' });
            return false;
        }
        
        // Replace historical cases
        setHistoricalCases(importedCases);
        
        // Update data source info
        setDataSource({
            type: 'custom',
            count: importedCases.length,
            label: `Custom Data (${importedCases.length} cases)`
        });
        
        const message = `Successfully imported ${importedCases.length} cases to Qdrant vector database.${skippedRows > 0 ? ` (${skippedRows} rows skipped due to errors)` : ''}`;
        setUploadStatus({ type: 'success', message });
        
        return true;
    }, [uploadedData]);
    
    // Reset to synthetic data
    const resetToSynthetic = useCallback(() => {
        resetHistoricalCases();
        setDataSource({
            type: 'synthetic',
            count: 1000,
            label: 'Synthetic Data (1,000 cases)'
        });
        setUploadedData(null);
        setFileHeaders([]);
        setUploadStatus({ type: 'info', message: 'Reset to synthetic data with 1,000 generated cases.' });
    }, []);
    
    // Handle file upload
    const handleFileUpload = useCallback((file) => {
        return new Promise((resolve, reject) => {
            const fileName = file.name.toLowerCase();
            const isExcel = fileName.endsWith('.xlsx') || fileName.endsWith('.xls');
            const isCSV = fileName.endsWith('.csv');
            
            if (!isExcel && !isCSV) {
                setUploadStatus({ type: 'error', message: 'Please upload a valid Excel (.xlsx, .xls) or CSV (.csv) file.' });
                reject(new Error('Invalid file type'));
                return;
            }
            
            setUploadStatus({ type: 'info', message: `Reading "${file.name}"...` });
            
            const reader = new FileReader();
            
            reader.onload = (e) => {
                try {
                    let result;
                    if (isExcel) {
                        result = parseExcel(e.target.result);
                    } else {
                        result = parseCSV(e.target.result);
                    }
                    
                    setFileHeaders(result.headers);
                    setUploadedData(result.data);
                    
                    const sheetInfo = result.sheetName && result.sheetCount > 1 ? ` (Sheet: "${result.sheetName}")` : '';
                    setUploadStatus({ 
                        type: 'success', 
                        message: `Loaded "${file.name}"${sheetInfo} with ${result.data.length} rows and ${result.headers.length} columns.` 
                    });
                    
                    resolve(result);
                } catch (err) {
                    console.error('File parsing error:', err);
                    setUploadStatus({ type: 'error', message: 'Error parsing file. Please ensure it is a valid file.' });
                    reject(err);
                }
            };
            
            reader.onerror = () => {
                setUploadStatus({ type: 'error', message: 'Error reading file. Please try again.' });
                reject(new Error('File read error'));
            };
            
            if (isExcel) {
                reader.readAsArrayBuffer(file);
            } else {
                reader.readAsText(file);
            }
        });
    }, []);
    
    const value = {
        // State
        activeTab,
        dataSource,
        applicationResults,
        isProcessing,
        uploadedData,
        fileHeaders,
        uploadStatus,
        
        // Actions
        setActiveTab,
        processApplication,
        getCaseCount,
        getStats,
        importDataFromFile,
        resetToSynthetic,
        handleFileUpload,
        setUploadStatus
    };
    
    return React.createElement(AppContext.Provider, { value }, children);
}
