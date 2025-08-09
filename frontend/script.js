document.addEventListener('DOMContentLoaded', () => {
    // Get references to all HTML elements
    const defaultDataRadio = document.getElementById('default-data');
    const uploadDataRadio = document.getElementById('upload-data');
    const defaultDataInfo = document.getElementById('default-data-info');
    const uploadArea = document.getElementById('upload-area');
    const requirementsToggle = document.getElementById('requirements-toggle');
    const dataRequirements = document.getElementById('data-requirements');
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const columnMappingArea = document.getElementById('column-mapping-area');
    const clusterCountInput = document.getElementById('cluster-count');
    const analyzeBtn = document.getElementById('analyze-btn');
    const statusDiv = document.getElementById('status');
    const plotDiv = document.getElementById('plot');
    const personaArea = document.getElementById('persona-area');
    const loaderOverlay = document.getElementById('loader-overlay');
    const infoBtn = document.getElementById('info-btn');
    const modalOverlay = document.getElementById('modal-overlay');
    const closeBtn = document.getElementById('close-btn');
    let uploadedFile = null;

    // UI Logic and Event Listeners
    [defaultDataRadio, uploadDataRadio].forEach(radio => {
        radio.addEventListener('change', () => {
            const isDefault = defaultDataRadio.checked;
            defaultDataInfo.classList.toggle('hidden', !isDefault);
            uploadArea.classList.toggle('hidden', isDefault);
            if (isDefault) {
                columnMappingArea.classList.add('hidden');
            }
        });
    });

    requirementsToggle.addEventListener('click', () => dataRequirements.classList.toggle('hidden'));
    dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('dragover'); });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            fileInput.files = e.dataTransfer.files;
            handleFileSelect(e.dataTransfer.files[0]);
        }
    });
    fileInput.addEventListener('change', () => { if (fileInput.files.length > 0) handleFileSelect(fileInput.files[0]); });
    
    // Functions for backend communication
    function handleFileSelect(file) {
        if (!file) return;
        uploadedFile = file;
        dropZone.querySelector('p').textContent = `File selected: ${file.name}`;
        const formData = new FormData();
        formData.append('file', file);
        statusDiv.textContent = 'Reading the spreadsheet...';
        fetch('https://customer-insights-api.onrender.com', { method: 'POST', body: formData })
            .then(response => response.json())
            .then(data => {
                statusDiv.textContent = '';
                if (data.headers) {
                    createColumnMappings(data.headers);
                } else {
                    statusDiv.textContent = `Error: ${data.error}`;
                }
            })
            .catch(error => {
                statusDiv.textContent = 'Error fetching column headers.';
                console.error(error);
            });
    }
    function createColumnMappings(headers) {
        columnMappingArea.innerHTML = '<p>Map your columns to the required RFM fields:</p>';
        const mappings = [
            { id: 'customer_id', label: 'Customer ID:' }, { id: 'invoice_id', label: 'Invoice ID:' },
            { id: 'invoice_date', label: 'Invoice Date:' }, { id: 'quantity', label: 'Quantity:' }, { id: 'price', label: 'Price:' }
        ];
        mappings.forEach(mapping => {
            const div = document.createElement('div');
            div.className = 'config-item';
            const label = document.createElement('label');
            label.setAttribute('for', mapping.id);
            label.textContent = mapping.label;
            const select = document.createElement('select');
            select.id = mapping.id;
            select.name = mapping.id;
            headers.forEach(header => {
                const option = document.createElement('option');
                option.value = header;
                option.textContent = header;
                select.appendChild(option);
            });
            div.appendChild(label);
            div.appendChild(select);
            columnMappingArea.appendChild(div);
        });
        columnMappingArea.classList.remove('hidden');
    }

    analyzeBtn.addEventListener('click', () => {
        // Show loader and clear previous results
        loaderOverlay.classList.remove('hidden');
        loaderOverlay.querySelector('p').textContent = 'Running the numbers. It\'s a whole thing...';
        statusDiv.textContent = '';
        plotDiv.innerHTML = '';
        personaArea.innerHTML = '';

        // Prepare configuration
        const config = {
            use_default: defaultDataRadio.checked,
            cluster_count: parseInt(clusterCountInput.value)
        };
        if (!config.use_default) {
            if (!uploadedFile) {
                statusDiv.textContent = 'Error: Please upload a file.';
                loaderOverlay.classList.add('hidden');
                return;
            }
            config.mappings = {
                customer_id: document.getElementById('customer_id').value,
                invoice_id: document.getElementById('invoice_id').value,
                invoice_date: document.getElementById('invoice_date').value,
                quantity: document.getElementById('quantity').value,
                price: document.getElementById('price').value,
            };
        }
        
        const formData = new FormData();
        formData.append('config', JSON.stringify(config));
        if (!config.use_default && uploadedFile) {
            formData.append('file', uploadedFile);
        }

        // Fetch data from backend
        fetch('https://customer-insights-api.onrender.com', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            loaderOverlay.classList.add('hidden');
            if (data.error) {
                statusDiv.textContent = `Error: ${data.error}`;
                return;
            }
            createPlot(data.plotData);
            displayPersonas(data.personaData);
        })
        .catch(error => {
            loaderOverlay.classList.add('hidden');
            console.error('There was a problem with the fetch operation:', error);
            statusDiv.textContent = 'Error: Could not fetch data from the server.';
        });
    });
    
    // Display Functions
    function displayPersonas(personas) {
        personas.forEach(p => {
            const card = document.createElement('div');
            card.className = 'persona-card';

            // ### THIS INNERHTML IS THE ONLY PART THAT CHANGES ###
            card.innerHTML = `
                <h3>
                    <span class="color-dot" style="background-color: ${COLOR_PALETTE[p.cluster_id % COLOR_PALETTE.length]}"></span>
                    ${p.persona}
                </h3>
                <p>${p.description}</p>
                <ul>
                    <li>
                        <span data-tooltip="How many days ago was their last purchase? (Lower is better)">Avg. Recency:</span>
                        ${p.avg_recency} days
                    </li>
                    <li>
                        <span data-tooltip="How many separate purchases have they made? (Higher is better)">Avg. Frequency:</span>
                        ${p.avg_frequency}
                    </li>
                    <li>
                        <span data-tooltip="What is their total spending? (Higher is better)">Avg. Monetary Value:</span>
                        ${p.avg_monetary.toFixed(2)}
                    </li>
                </ul>
            `;
            personaArea.appendChild(card);
        });
    }
    const COLOR_PALETTE = ['#8A2BE2', '#4A90E2', '#50E3C2', '#F5A623', '#E0204D', '#34A853', '#F4B400', '#EA4335'];
    function createPlot(data) {
        const tableData = data.data;
        const recency = tableData.map(row => row.Recency);
        const frequency = tableData.map(row => row.Frequency);
        const monetary = tableData.map(row => row.MonetaryValue);
        const clusters = tableData.map(row => row.Cluster);
        const pointColors = clusters.map(c => COLOR_PALETTE[c % COLOR_PALETTE.length]);
        const trace = {
            x: recency, y: frequency, z: monetary, mode: 'markers', type: 'scatter3d',
            marker: { color: pointColors, size: 5, opacity: 0.8 }
        };
        const layout = {
            title: { text: '3D Customer Segments (RFM)', font: { color: '#EAEAEA' } },
            paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
            margin: { l: 0, r: 0, b: 0, t: 40 },
            scene: {
                xaxis: { title: 'Recency (Days)', color: '#B3B3B3', gridcolor: '#2c2c2c' },
                yaxis: { title: 'Frequency', color: '#B3B3B3', gridcolor: '#2c2c2c' },
                zaxis: { title: 'Monetary Value (€)', color: '#B3B3B3', gridcolor: '#2c2c2c' }
            }
        };
        Plotly.newPlot('plot', [trace], layout);
    }


    // Event listeners for the 'About' modal
    infoBtn.addEventListener('click', () => {
        modalOverlay.classList.remove('hidden');
    });

    closeBtn.addEventListener('click', () => {
        modalOverlay.classList.add('hidden');
    });

    // Also close the modal if the user clicks the dark overlay
    modalOverlay.addEventListener('click', (e) => {
        if (e.target === modalOverlay) {
            modalOverlay.classList.add('hidden');
        }
    });
});