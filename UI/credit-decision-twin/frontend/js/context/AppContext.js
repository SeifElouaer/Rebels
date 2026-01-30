// React Context for global state management

const { createContext, useContext, useState, useCallback, useEffect } = React;

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
    
    // API connection status
    const [apiStatus, setApiStatus] = useState({
        api_status: 'connecting',
        qdrant_status: 'connecting',
        case_count: 0
    });
    
    // Data source state
    const [dataSource, setDataSource] = useState({
        type: 'none',
        count: 0,
        label: 'No data loaded'
    });
    
    // Application results state
    const [applicationResults, setApplicationResults] = useState(null);
    
    // Loading state
    const [isProcessing, setIsProcessing] = useState(false);
    
    // Upload state
    const [fileHeaders, setFileHeaders] = useState([]);
    const [previewData, setPreviewData] = useState([]);
    const [uploadStatus, setUploadStatus] = useState(null);
    
    // Check API status on mount and periodically
    useEffect(() => {
        const checkStatus = async () => {
            const status = await api.getStatus();
            setApiStatus(status);
            
            const source = await api.getDataSource();
            setDataSource(source);
        };
        
        checkStatus();
        const interval = setInterval(checkStatus, 30000); // Check every 30 seconds
        
        return () => clearInterval(interval);
    }, []);
    
    // Get current case count
    const getCaseCount = useCallback(() => {
        return dataSource.count;
    }, [dataSource]);
    
    // Refresh data source info
    const refreshDataSource = useCallback(async () => {
        const source = await api.getDataSource();
        setDataSource(source);
        return source;
    }, []);
    
    // Process a credit application
    const processApplication = useCallback(async (applicant) => {
        setIsProcessing(true);
        setApplicationResults(null);
        
        try {
            const results = await api.processApplication(applicant);
            setApplicationResults(results);
            return results;
        } catch (error) {
            setUploadStatus({ type: 'error', message: error.message });
            throw error;
        } finally {
            setIsProcessing(false);
        }
    }, []);
    
    // Handle file upload
    const handleFileUpload = useCallback(async (file) => {
        setUploadStatus({ type: 'info', message: `Uploading "${file.name}"...` });
        
        try {
            const result = await api.uploadFile(file);
            
            setFileHeaders(result.headers);
            setPreviewData(result.preview);
            
            setUploadStatus({ 
                type: 'success', 
                message: `Loaded "${result.filename}" with ${result.row_count.toLocaleString()} rows and ${result.headers.length} columns.` 
            });
            
            return result;
        } catch (error) {
            setUploadStatus({ type: 'error', message: error.message });
            throw error;
        }
    }, []);
    
    // Import dataset from uploaded file
    const importDataFromFile = useCallback(async (mappings) => {
        setUploadStatus({ type: 'info', message: 'Importing dataset to Qdrant...' });
        
        try {
            const result = await api.importDataset(mappings);
            
            // Refresh data source
            await refreshDataSource();
            
            const message = `${result.message}${result.skipped_rows > 0 ? ` (${result.skipped_rows} rows skipped)` : ''}`;
            setUploadStatus({ type: 'success', message });
            
            // Clear preview
            setPreviewData([]);
            
            return true;
        } catch (error) {
            setUploadStatus({ type: 'error', message: error.message });
            return false;
        }
    }, [refreshDataSource]);
    
    // Clear all data
    const clearAllData = useCallback(async () => {
        try {
            await api.clearData();
            await refreshDataSource();
            
            setFileHeaders([]);
            setPreviewData([]);
            setApplicationResults(null);
            setUploadStatus({ type: 'info', message: 'All data cleared. Please upload a new dataset.' });
        } catch (error) {
            setUploadStatus({ type: 'error', message: error.message });
        }
    }, [refreshDataSource]);
    
    const value = {
        // State
        activeTab,
        apiStatus,
        dataSource,
        applicationResults,
        isProcessing,
        fileHeaders,
        previewData,
        uploadStatus,
        
        // Actions
        setActiveTab,
        processApplication,
        getCaseCount,
        refreshDataSource,
        importDataFromFile,
        clearAllData,
        handleFileUpload,
        setUploadStatus
    };
    
    return React.createElement(AppContext.Provider, { value }, children);
}
