import React, { useState, useEffect } from 'react';
import Chart from 'react-apexcharts';
import '../App.css';

const PredictionResult = ({ predictions }) => {
    const [viewMode, setViewMode] = useState('table');

    const [chartOptions, setChartOptions] = useState({
        chart: { type: 'line', zoom: { enabled: true } },
        xaxis: { categories: [], title: { text: 'Date' } },
        yaxis: {
            title: { text: 'Price' },
            labels: { formatter: (value) => value.toFixed(3) },
        },
        title: { text: 'Price Predictions', align: 'center' },
    });

    const [series, setSeries] = useState([{ name: 'Predicted Price', data: [] }]);

    useEffect(() => {
        if (predictions.length > 0) {
            const dates = predictions.map((item) => item.date);
            const prices = predictions.map((item) => item.predicted_price);

            setChartOptions((prev) => ({
                ...prev,
                xaxis: { ...prev.xaxis, categories: dates },
            }));

            setSeries([{ name: 'Predicted Price', data: prices }]);
        }
    }, [predictions]);

    return (
        <div>
            <div className="view-mode-buttons">
                <button
                    onClick={() => setViewMode('table')}
                    className={viewMode === 'table' ? 'selected' : ''}
                >
                    Table
                </button>
                <button
                    onClick={() => setViewMode('chart')}
                    className={viewMode === 'chart' ? 'selected' : ''}
                >
                    Chart
                </button>
            </div>
            {viewMode === 'table' && (
                <div className="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Price</th>
                            </tr>
                        </thead>
                        <tbody>
                            {predictions.map((row, index) => (
                                <tr key={index}>
                                    <td>{row.date}</td>
                                    <td>{row.predicted_price.toFixed(3)}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
            {viewMode === 'chart' && (
                <Chart options={chartOptions} series={series} type="line" />
            )}
        </div>
    );
};

export default PredictionResult;
