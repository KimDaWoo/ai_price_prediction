import React, { useState, useEffect } from 'react';
import axios from 'axios';
import PredictionResult from './PredictionResult';
import '../App.css';
import toast from 'react-hot-toast';

// 로딩 이미지를 import
import loadingImage from '../assets/graphics.png';
import LogoImage from '../assets/favicon.png';

const MaterialRegionSelector = () => {
    const notifyNotSelected = () => toast.error('자재와 지역 선택은 필수!', { duration: 3000 });
    
    const [materials, setMaterials] = useState({});
    const [selectedMaterial, setSelectedMaterial] = useState('');
    const [selectedRegion, setSelectedRegion] = useState('');
    const [regions, setRegions] = useState([]);
    const [predictions, setPredictions] = useState([]);
    const [onPredictions, setOnPredictions] = useState(false);
    const [onFirst, setOnFirst] = useState(true);

    useEffect(() => {
        axios.get(`${process.env.REACT_APP_API_URL}/materials`)
            .then((response) => {
                setMaterials(response.data);
            })
            .catch((error) => console.error('Error fetching materials:', error));
    }, []);

    const handleMaterialChange = (e) => {
        const material = e.target.value;
        setSelectedMaterial(material);
        setRegions(materials[material]?.[1] || []);
        setSelectedRegion('');
    };

    const handleRegionChange = (e) => {
        setSelectedRegion(e.target.value);
    };
    
    const handlePredict = () => {
        if (!selectedMaterial || !selectedRegion) {
            notifyNotSelected();
            return;
        }

        if(onFirst) {
            setOnFirst(false)
        }

        setOnPredictions(true);
    
        toast.promise(
            axios.post(`${process.env.REACT_APP_API_URL}/predict`, {
                material: selectedMaterial,
                region: selectedRegion,
            })
            .then((response) => {
                setPredictions(response.data.predictions || []);
                setOnPredictions(false);
            })
            .catch(() => {
                setOnPredictions(false);
            }),
            {
                loading: '예측 중 ...',
                success: '예측 성공! 결과를 확인해주세요.',
                error: '예측 실패.. 다시 시도해보세요!',
            }
        );
    };

    return (
        <div className="material-region-selector">
            <div style={{ display: 'flex', textAlign: 'left', flexDirection: 'row', gap: "12px", alignItems: 'center'}}>
                <img src={LogoImage} alt="Logo" style={{width: "36px", height: "36px"}}/>
                <h1>자재로 - 건자재 예측 AI</h1>
            </div>
            <div className="material-region-selector-main">
                <div className="select-area">
                    <div>
                        <select
                            id="material"
                            onChange={handleMaterialChange}
                            value={selectedMaterial}
                            className={!selectedMaterial ? 'dropdown-default' : 'dropdown-selected'}
                        >
                            <option value="">-- Select Material --</option>
                            {Object.keys(materials).map((material) => (
                                <option key={material} value={material}>
                                    {material}
                                </option>
                            ))}
                        </select>
                    </div>
                    <div>
                        <div>
                            <select
                                id="region"
                                onChange={handleRegionChange}
                                value={selectedRegion}
                                disabled={!regions.length}
                                className={!selectedRegion ? 'dropdown-default' : 'dropdown-selected'}
                            >
                                <option value="">-- Select Region --</option>
                                {regions.map((region) => (
                                    <option key={region} value={region}>
                                        {region}
                                    </option>
                                ))}
                            </select>
                        </div>
                        <button
                            onClick={handlePredict}
                            className={!selectedMaterial || !selectedRegion || onPredictions ? 'disabled-button' : 'active-button'}
                            disabled={onPredictions}
                        >
                            Predict Price
                        </button>
                    </div>
                </div>
                <div>
                    {onPredictions || onFirst ? (
                        <div className="loading-container">
                            <img src={loadingImage} alt="Loading..." />
                        </div>
                    ) : (
                        <PredictionResult predictions={predictions} />
                    )}
                </div>
            </div>
        </div>
    );
};

export default MaterialRegionSelector;
