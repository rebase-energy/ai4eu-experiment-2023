


const inputFormTrain = document.getElementById('input_form_train');
const inputFormPredict = document.getElementById('input_form_predict');
const trainInput = document.getElementById('train_file');
const predInput = document.getElementById('pred_file');
const btnTrain = document.getElementById('btn_train');
const btnPredict = document.getElementById('btn_predict');
const btnIncrReg = document.getElementById('btn_regime_incr');
const btnDecrReg = document.getElementById('btn_regime_decr');
const nrRegimes = document.getElementById('regime_nr');


const colors = [
    '#003f5c',
    '#7a5195',
    '#ef5675',
    '#ffa600',
]

const makeDatasets = (rows) => {
    const datasetValues = {};
    rows.forEach(row => {
        for (let key in row){
            if (key !== 'timestamp'){
                const r = {x: row.timestamp, y: row[key]}
                datasetValues[key] = key in datasetValues ? [...datasetValues[key], r] : [r];
                
            }
        }
    })

    const datasets = Object.keys(datasetValues).map((key, index) => {
        return ({
            label: key,
            pointRadius: 0,
            data: datasetValues[key],
            borderColor: colors[index]
        })
    })


    return datasets;
}

inputFormTrain.onsubmit = async (e) => {
    e.preventDefault();

    await runCalcWeights();
}

inputFormPredict.onsubmit = async (e) => {
    e.preventDefault();

    await calcWeightedMean();
}


btnIncrReg.onclick = () => {
    const newValue = parseInt(nrRegimes.innerText)+1;
    if (newValue <= 23){
        nrRegimes.innerText = newValue;
    }
}

btnDecrReg.onclick = () => {
    const newValue = parseInt(nrRegimes.innerText)-1;
    if (newValue >= 0){
        nrRegimes.innerText = newValue;
    }
}


const pollResults = async () => {
    const resp = await fetch('/result');
    if (resp.status === 200){
        const data = await resp.json();
        if (data.timestamp !== predTimestamp){
            const result = data['prediction'];
            const datasets = makeDatasets(result);
            myChart.data = {datasets: datasets};
            myChart.update();
            predTimestamp = data.timestamp;
            lastRunSpan.textContent = `${predTimestamp}`;
        }

    };
    setTimeout(pollResults, 5000);
}

// pollResults();


const createWeightTable = (rows) => {
    const tbodyEl = document.getElementById('weight-table')
    tbodyEl.innerHTML = "";
    rows.forEach(row => {
        const rowEl = document.createElement('tr');

        const cols = [
            `${row.from}-${row.to}`,
            row.provider_a,
            row.provider_b
        ];
        cols.forEach(col => {
            const cell = document.createElement('td');
            cell.appendChild(document.createTextNode(col))
            rowEl.appendChild(cell);
        })

        tbodyEl.appendChild(rowEl)
    })


}


const calcWeightedMean = async () => {
    try {
        btnPredict.style.opacity = 0.5;
        btnPredict.style.pointerEvents = 'none';
        const data = new FormData()

        data.append('pred_file', predInput.files[0], predInput.files[0].name)

        const options = {
            method: 'POST',
            body: data
        }
        const resp = await fetch(`/calculate_mean`, options);
        const result = await resp.json();

        console.log('result :>> ', result);
        const datasets = makeDatasets(result);
        myChart.data = {datasets: datasets};
        myChart.update();
        console.log('myChart :>> ', myChart);

    }
    catch (e) {
        console.log(e);
    }
    finally {
        btnPredict.style.opacity = 1;
        btnPredict.style.pointerEvents = 'auto';
    }
}


const runCalcWeights = async () => {
    try {
        btnTrain.style.opacity = 0.5;
        btnTrain.style.pointerEvents = 'none';
        const data = new FormData()

        data.append('train_file', trainInput.files[0], trainInput.files[0].name)
        data.append('nr_regimes', nrRegimes.innerText);
        //data.append('pred_file', predInput.files[0], predInput.files[0].name)

        const options = {
            method: 'POST',
            body: data
        }
        const resp = await fetch(`/calculate_weights`, options);
        const rows = await resp.json();

        createWeightTable(rows);
    }
    catch (e) {
        console.log(e);
    }
    finally {
        btnTrain.style.opacity = 1;
        btnTrain.style.pointerEvents = 'auto';
    }

}