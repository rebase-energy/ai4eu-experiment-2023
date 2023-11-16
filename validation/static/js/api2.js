


const inputForm = document.getElementById('input_form');
const fileData = document.getElementById('data_file');
const btnUpload = document.getElementById('btn_upload');
const colsInput = document.getElementById('input_columns');
const expectationsList = document.getElementById('expectations_list');
const btnAdd = document.getElementById('btn-add');
const rowCounter = document.getElementById('row-counter');

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


fileData.onchange = async () => {
    //inputForm.submit();
    await checkColumns();
};

btnAdd.onclick = (e) => {
    e.preventDefault();
    newExpectationRow();
}


inputForm.onsubmit = async (e) => {
    e.preventDefault();

    await runValidate();
}



const createTable = (data, validationResult) => {
    const theadEl = document.getElementById('result-thead')
    const tbodyEl = document.getElementById('result-tbody')
    theadEl.innerHTML = "";
    tbodyEl.innerHTML = "";
    const cols = Object.keys(data[0]);

    const trHeadEl = document.createElement('tr');
    cols.forEach(col => {
        const th = trHeadEl.appendChild(document.createElement('th'));
        th.appendChild(document.createTextNode(col))
        th.style = "position: sticky; top: 0;";
        theadEl.appendChild(th);
    })
    theadEl.appendChild(trHeadEl);

    data.forEach((row, index) => {
        const rowEl = document.createElement('tr');

        cols.forEach(col => {
            const cell = document.createElement('td');
            const v = row[col];
            cell.appendChild(document.createTextNode(v))

            validationResult.results.forEach(result => {
                if (col === result.expectation_config.kwargs.column){
                    if (result.result.partial_unexpected_index_list.find(i => i===index)){
                        cell.classList.add("cell-error")
                    }
                }
            })


            rowEl.appendChild(cell);
        })

        tbodyEl.appendChild(rowEl)
    })


}


const newExpectationRow = () => {
    const i = parseInt(rowCounter.value);

    const cols = JSON.parse(colsInput.value);


    const div = document.createElement('div');
    div.style = "display: flex; flex-direction: row; align-items: center; gap: 8px"

    div.appendChild(document.createTextNode('Expect'));
    div.id = `expect_${i}`;

    const select = document.createElement('select');
    select.id = `select_${i}`;
    cols.forEach(col => {
        const opt = document.createElement('option');
        opt.value = col;
        opt.text = col;
        select.append(opt)
    })
    div.appendChild(select)
    div.appendChild(document.createTextNode('to be between'));

    const inpMin = document.createElement('input');
    inpMin.id = `inpMin_${i}`;
    inpMin.style = 'width: 120px;'
    div.appendChild(inpMin);
    div.appendChild(document.createTextNode('and'));
    const inpMax = document.createElement('input');
    inpMax.id = `inpMax_${i}`;
    inpMax.style = 'width: 120px;'
    div.appendChild(inpMax);
    expectationsList.appendChild(div);
    
    if (expectationsList.children.length === 1){
        btnAdd.style.visibility = 'visible';
    }

    rowCounter.value = i+1;

    

}

const checkColumns = async () => {
    const data = new FormData();
    data.append('file', fileData.files[0], fileData.files[0].name);

    const options = {
        method: 'POST',
        body: data
    }
    const resp = await fetch(`/check_columns`, options);
    const columns = await resp.text();

    colsInput.value = columns;



    newExpectationRow();
    

}


const runValidate = async () => {
    try {
        btnUpload.style.opacity = 0.5;
        btnUpload.style.pointerEvents = 'none';

        const data = new FormData();
        const expectations = []

        let i = 0;
        for (let child of expectationsList.children) {
            const sel = child.children[0];
            const min = child.children[1];
            const max = child.children[2];

            expectations.push({
                'expectation': 'expect_column_values_to_be_between', 
                'args': [
                    sel.value,
                    parseFloat(min.value),
                    parseFloat(max.value)
                ]
            })

            i++;
        }

        console.log('expectations :>> ', expectations);

        data.append('expectations', JSON.stringify(expectations));

        const options = {
            method: 'POST',
            body: data
        }
        const resp = await fetch(`/validate`, options);
        const path = await resp.json();


        const resp2 = await fetch(path);

        const expResult = await resp2.json();


        const key = Object.keys(expResult.validation.run_results)[0];
        const validationResult = expResult.validation.run_results[key].validation_result;

        createTable(expResult.data, validationResult);




        // const datasets = makeDatasets(result);
        // myChart.data = {datasets: datasets};
        // myChart.update();
        // console.log('myChart :>> ', myChart);

    }
    catch (e) {
        console.log(e);
    }
    finally {
        btnUpload.style.opacity = 1;
        btnUpload.style.pointerEvents = 'auto';
    }
}

