


const inputFormTrain = document.getElementById('input_form_train');
const inputFormPredict = document.getElementById('input_form_predict');
const trainInput = document.getElementById('train_file');
const predInput = document.getElementById('pred_file');
const btnTrain = document.getElementById('btn_train');
const btnPredict = document.getElementById('btn_predict');
const nrSteps = document.getElementById('input_nr_steps');

const colors = [
    '#003f5c',
    '#7a5195',
    '#ef5675',
    '#ffa600',
]

const makeDatasets = (rows) => {
    const datasetsObj = {}

    rows.forEach((row, index) => {
        for (let key in row){
            if (!(key in datasetsObj)){
                datasetsObj[key] = [{x: index, y: row[key]}];
            }
            else {
                datasetsObj[key].push(
                    {x: index, y: row[key]}
                )
            }
        }
    })

    const datasets = Object.keys(datasetsObj).map((key, index) => {
        return ({
            label: key,
            pointRadius: 0,
            data: datasetsObj[key],
            borderColor: colors[index]
        })
    })

    console.log('datasets :>> ', datasets);


    return datasets;
}

inputFormTrain.onsubmit = async (e) => {
    e.preventDefault();

    await runTrain();
}

inputFormPredict.onsubmit = async (e) => {
    e.preventDefault();

    await runPredict();
}

const createPredTable = (rows) => {
    const tbodyEl = document.getElementById('pred-table')
    const theadEl = document.getElementById('pred-table-head');

    tbodyEl.innerHTML = "";

    const cols = ['Step', ...(Object.keys(rows[0]))];

    const trHead = document.createElement('tr');
    cols.forEach(c => {
        const th = document.createElement('th');
        th.appendChild(document.createTextNode(c));
        trHead.appendChild(th);
    })

    theadEl.appendChild(trHead);
   
    rows.forEach((row, index) => {
        const rowEl = document.createElement('tr');

        cols.forEach(col => {
            let v = index;
            if (col !== 'Step'){
                v = row[col];
            }
            const cell = document.createElement('td');
            cell.appendChild(document.createTextNode(v))
            rowEl.appendChild(cell);
        })

        tbodyEl.appendChild(rowEl)
    })


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




const runPredict = async () => {
    try {
        btnPredict.style.opacity = 0.5;
        btnPredict.style.pointerEvents = 'none';
        const data = new FormData()
        
        console.log('nrSteps.value :>> ', nrSteps.value);

        data.append('pred_file', predInput.files[0], predInput.files[0].name)
        data.append('nr_steps', nrSteps.value);

        const options = {
            method: 'POST',
            body: data
        }
        const resp = await fetch(`/predict`, options);
        const result = await resp.json();

        console.log('result :>> ', result);

        createPredTable(result);
        const datasets = makeDatasets(result);
        myChart.data = {datasets: datasets};
        myChart.update();

    }
    catch (e) {
        console.log(e);
    }
    finally {
        btnPredict.style.opacity = 1;
        btnPredict.style.pointerEvents = 'auto';
    }
}


const runTrain = async () => {
    try {
        btnTrain.style.opacity = 0.5;
        btnTrain.style.pointerEvents = 'none';
        const data = new FormData()

        data.append('train_file', trainInput.files[0], trainInput.files[0].name)
        //data.append('pred_file', predInput.files[0], predInput.files[0].name)

        const options = {
            method: 'POST',
            body: data
        }
        const resp = await fetch(`/train`, options);
        const rows = await resp.json();

    }
    catch (e) {
        console.log(e);
    }
    finally {
        btnTrain.style.opacity = 1;
        btnTrain.style.pointerEvents = 'auto';
    }

}