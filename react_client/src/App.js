import React from 'react';
import MaterialRegionSelector from './components/MaterialRegionSelector';
import './App.css'
import { Toaster } from 'react-hot-toast';

function App() {
    return (
        <div className="App">
            <Toaster position="top-center" reverseOrder={false} />
            <MaterialRegionSelector />
        </div>
    );
}

export default App;
