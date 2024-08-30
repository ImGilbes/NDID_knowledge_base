
function array_remove(array,value){
    const index = array.indexOf(value);
    if (index > -1) { // only splice array when item is found
        array.splice(index, 1); // 2nd parameter means remove one item only
    }
    return array;
}

function add_goto_specific(entity){
    async function handleEntryClick(event) {
        await fetch('/set_specific?entity=' + entity + '&def=' + event.target.textContent);
        window.location.href = "/specific";
    }

    const rows = document.getElementById(entity+'_table').querySelectorAll('table tr');

    rows.forEach(row => {
        const tds = row.querySelectorAll('td'); // Get all <td> elements in the row
        
        if (tds.length > 0) {
            // Assign the function to the first <td>
            tds[0].addEventListener('click', handleEntryClick);
        }

        if (tds.length > 1) {
            // Assign the class to the second <td>
            tds[1].classList.add("secondColumnClass");
        }
    });
}

async function loadTable(entity) {

    const response = await fetch('/get_table?entity=' + entity);
    const data = await response.json();
    var table_html = data.table_html;

    document.getElementById(entity+'_table').innerHTML = table_html;

    add_goto_specific(entity);
    
    addToLoaded(entity);

    updateFilters();
}



function addToLoaded(entity){
    if (loaded.indexOf(entity) == -1){
        loaded.push(entity);
    }
}
function addToDisplayed(entity){
    if (displayed.indexOf(entity) == -1){
        displayed.push(entity);
    }
}

function add_table(entity,table,related_flag, div_name){}

async function getTablesConnections() {
    const response = await fetch('/get_specific');
    const data = await response.json();

    if(data.starting_record && data.entity){
        current_main_entity = data.entity;
        addToLoaded(data.entity); addToDisplayed(data.entity);

        let tmp_div = document.createElement("div");
        // use this block template for every entity table
        new_html_block = `<div class="container" id="${current_main_entity}_container">
            
            <div class="content" id="item_content">
                <div id="${current_main_entity}_table"></div>
            </div>
        </div>`;
        tmp_div.innerHTML=new_html_block;

        document.getElementById("starting_record_table").appendChild(tmp_div);
        document.getElementById(`${current_main_entity}_table`).innerHTML = data.starting_record;
        document.getElementById("starting_record_container").style.display = "block";
    }
    else
        console.log("there is no starting record for some reason!");
    
    if(data.entities && data.tables){

        var tables = [...data.tables]; // this thing somehow converts a stringified list to an array
        var entities = [...data.entities];

        if(tables.length == entities.length){

            for (let i = 0; i < tables.length; i++) {

                let tmp_div = document.createElement("div");
                // use this block template for every entity table
                new_html_block = `<div class="container" id="${entities[i]}_container">
                    <div class="content" id="item_name_container">
                        <p id="${entities[i]}_name">Related ${entities[i]}</p>
                        <p id="${entities[i]}_definition">The matched categories are highlighted in green &#128994</p>
                    </div>
                    <div class="content" id="item_content">
                        <div id="${entities[i]}_table">${tables[i]}</div>
                    </div>
                </div>`;
                tmp_div.innerHTML=new_html_block;

                // document.getElementById("where-all-tables-go").innerHTML += new_html_block; 
                //only using appendchild i can update the dom on the spot and search with get element by id
                document.getElementById("where-all-tables-go").appendChild(tmp_div);

                if(entities[i]){
                    addToLoaded(entities[i]); addToDisplayed(entities[i]);
                }

                add_goto_specific(entities[i]);
                
                var abc = [...data.shared_cats];
                var headersToHighlight = abc[i];
                
                if(headersToHighlight){
                    const table = document.getElementById(`${entities[i]}_table`);
                    const headerCells = table.querySelectorAll("thead th");

                    headerCells.forEach((cell, index) => {
                        if (headersToHighlight.includes(cell.textContent.trim())) {
                            // If the header matches, highlight the entire column in the tbody
                            const rows = table.querySelectorAll("tbody tr");
                            rows.forEach(row => {
                                const cellToHighlight = row.cells[index];
                                cellToHighlight.classList.add("highlight");
                            });
                        }
                    });
                }
                else
                    console.log("No highlighting for some reason");
            }                    
        }
    }
    else
        alert("luckily this is not working");

    resetFilters();
}