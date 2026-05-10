document.addEventListener('DOMContentLoaded', () => {
    // Navigation Logic
    const navBtns = document.querySelectorAll('.nav-btn');
    const viewSections = document.querySelectorAll('.view-section');

    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all
            navBtns.forEach(b => b.classList.remove('active'));
            viewSections.forEach(v => v.classList.remove('active'));
            viewSections.forEach(v => v.classList.add('hidden'));

            // Add active class to clicked
            btn.classList.add('active');
            const targetId = btn.getAttribute('data-target');
            const targetView = document.getElementById(targetId);
            targetView.classList.remove('hidden');
            targetView.classList.add('active');
            
            // Resize plotly if switching to visualizer
            if(targetId === 'visualizer-view' && document.getElementById('plotly-chart').data) {
                Plotly.Plots.resize('plotly-chart');
            }
        });
    });

    // API Integration
    const patientSelect = document.getElementById('patient-select');
    const analyzeBtn = document.getElementById('analyze-btn');
    const btnText = document.getElementById('btn-text');
    const btnLoader = document.getElementById('btn-loader');
    const API_BASE = "http://127.0.0.1:8000";

    // Load Patients
    fetch(`${API_BASE}/api/patients`)
        .then(res => res.json())
        .then(data => {
            patientSelect.innerHTML = '<option value="">-- Select a Dataset --</option>';
            if(data.patients && data.patients.length > 0) {
                data.patients.forEach(p => {
                    const option = document.createElement('option');
                    option.value = p.id;
                    option.textContent = p.display_name;
                    patientSelect.appendChild(option);
                });
                analyzeBtn.disabled = false;
            } else {
                patientSelect.innerHTML = '<option value="">No datasets found in data/</option>';
            }
        })
        .catch(err => {
            console.error(err);
            patientSelect.innerHTML = '<option value="">Error loading datasets</option>';
        });

    // Run Analysis
    analyzeBtn.addEventListener('click', async () => {
        const filePath = patientSelect.value;
        if (!filePath) {
            alert('Please select a dataset first.');
            return;
        }

        // UI Loading State
        analyzeBtn.disabled = true;
        btnText.classList.add('hidden');
        btnLoader.classList.remove('hidden');

        try {
            const response = await fetch(`${API_BASE}/api/analyze`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ file_path: filePath })
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Analysis failed');
            }

            const data = await response.json();
            updateDashboard(data);
            plotChart(data);

        } catch (error) {
            console.error(error);
            alert(`Error: ${error.message}`);
        } finally {
            // Restore UI
            analyzeBtn.disabled = false;
            btnText.classList.remove('hidden');
            btnLoader.classList.add('hidden');
        }
    });

    function updateDashboard(data) {
        document.getElementById('arima-anom').textContent = data.arima.anomalies_detected;
        document.getElementById('arima-time').textContent = data.arima.time;

        document.getElementById('armax-anom').textContent = data.armax.anomalies_detected;
        document.getElementById('armax-time').textContent = data.armax.time;

        document.getElementById('kalman-anom').textContent = data.kalman.anomalies_detected;
        document.getElementById('kalman-time').textContent = data.kalman.time;
    }

    function plotChart(data) {
        const chartDiv = document.getElementById('plotly-chart');
        chartDiv.innerHTML = ''; // clear placeholder

        const signal = data.signal;
        const x = Array.from({length: signal.length}, (_, i) => i);
        
        // Extract anomaly indices
        const getAnomalyCoords = (flags) => {
            const xCoords = [];
            const yCoords = [];
            flags.forEach((flag, i) => {
                if(flag) {
                    xCoords.push(i);
                    yCoords.push(signal[i]);
                }
            });
            return {x: xCoords, y: yCoords};
        };

        const arimaCoords = getAnomalyCoords(data.arima.flags);
        const armaxCoords = getAnomalyCoords(data.armax.flags);
        const kalmanCoords = getAnomalyCoords(data.kalman.flags);

        const traceSignal = {
            x: x,
            y: signal,
            mode: 'lines',
            name: 'Raw EEG Signal',
            line: {color: '#94a3b8', width: 1}
        };

        const traceArima = {
            x: arimaCoords.x,
            y: arimaCoords.y,
            mode: 'markers',
            name: 'ARIMA Anomalies',
            marker: {color: '#ef4444', size: 6, opacity: 0.7}
        };

        const traceArmax = {
            x: armaxCoords.x,
            y: armaxCoords.y,
            mode: 'markers',
            name: 'ARMAX Anomalies',
            marker: {color: '#a855f7', size: 6, opacity: 0.7}
        };

        const traceKalman = {
            x: kalmanCoords.x,
            y: kalmanCoords.y,
            mode: 'markers',
            name: 'Kalman Filter Anomalies',
            marker: {color: '#10b981', size: 6, opacity: 0.7}
        };

        const layout = {
            plot_bgcolor: 'transparent',
            paper_bgcolor: 'transparent',
            font: {color: '#f8fafc', family: 'Inter'},
            margin: {l: 40, r: 20, t: 30, b: 40},
            xaxis: {
                title: 'Time (Samples)',
                gridcolor: 'rgba(255,255,255,0.1)',
                zerolinecolor: 'rgba(255,255,255,0.2)'
            },
            yaxis: {
                title: 'Amplitude',
                gridcolor: 'rgba(255,255,255,0.1)',
                zerolinecolor: 'rgba(255,255,255,0.2)'
            },
            shapes: [
                {
                    type: 'line',
                    x0: data.seizure_start_index,
                    x1: data.seizure_start_index,
                    y0: 0,
                    y1: 1,
                    yref: 'paper',
                    line: {
                        color: 'rgba(239, 68, 68, 0.8)', // red
                        width: 2,
                        dash: 'dot'
                    }
                }
            ],
            annotations: [
                {
                    x: data.seizure_start_index,
                    y: 1.05,
                    xref: 'x',
                    yref: 'paper',
                    text: 'Clinical Seizure Onset',
                    showarrow: false,
                    font: {color: '#ef4444'}
                }
            ],
            legend: {
                orientation: 'h',
                y: -0.2
            }
        };

        Plotly.newPlot(chartDiv, [traceSignal, traceArima, traceArmax, traceKalman], layout, {responsive: true});
    }
});
