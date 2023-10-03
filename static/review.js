let startTimestamp;
let endTimestamp;
let position;

function show_history_overview(start, end) {
    $.ajax({
        type: "GET",
        url: `/hand_history_overview?start=${start}&end=${end}`,
        dataType: "html",
        success: function(data, status) {
            console.log(data)
            $("#table-container").html(data);
        },
    });
}

function plot_performance_chart(data){

    // Creating an array for the x-axis (hand counts)
    const hands = Array.from({length: data.pnl.length}, (_, index) => index + 1);
    console.log(hands)

    const trace1 = {
        x: hands,
        y: data.pnl,
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Winloss',
        marker: {
            color: 'green',
            size: 10
        },
        line: {
            color: 'green',
            width: 3
        }
    };

    const trace2 = {
        x: hands,
        y: data.all_in_ev,
        type: 'scatter',
        mode: 'lines+markers',
        name: 'All-In EV',
        marker: {
            color: 'red',
            size: 10
        },
        line: {
            color: 'red',
            width: 3
        }
    };

    const layout = {
        title: 'History Performance',
        plot_bgcolor: "#2c2c2c",
        paper_bgcolor: "#2c2c2c",
        font: {
            color: "#ccc"
        },
        xaxis: {
            // ... (rest of your existing xaxis properties)
            gridcolor: "#444",
            title: {
                text: 'Hand Count',
                font: {
                    color: '#ccc'
                }
            }
        },
        yaxis: {
            // ... (rest of your existing yaxis properties)
            gridcolor: "#444",
            title: {
                text: 'Value',
                font: {
                    color: '#ccc'
                }
            }
        }
    };

    Plotly.newPlot('history-performance-container', [trace1, trace2], layout);

}

function plot_hole_cards_performance(){
    const number = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
    let annotations =  []
    const data = [{
        z: [
            [1, 20, 30, 1, 20, 30, 1, 20, 30, 1, 20, 30, 1],
            [20, 1, 60, 1, 20, 30, 1, 20, 30, 1, 20, 30, 1],
            [30, 60, 1, 1, 20, 30, 1, 20, 30, 1, 20, 30, 1],
            [30, 60, 1, 1, 20, 30, 1, 20, 30, 1, 20, 30, 1],
            [30, 60, 1, 1, 20, 30, 1, 20, 30, 1, 20, 30, 1],
            [30, 60, 1, 1, 20, 30, 1, 20, 30, 1, 20, 30, 1],
            [30, 60, 1, 1, 20, 30, 1, 20, 30, 1, 20, 30, 1],
            [30, 60, 1, 1, 20, 30, 1, 20, 30, 1, 20, 30, 1],
            [30, 60, 1, 1, 20, 30, 1, 20, 30, 1, 20, 30, 1],
            [30, 60, 1, 1, 20, 30, 1, 20, 30, 1, 20, 30, 1],
            [30, 60, 1, 1, 20, 30, 1, 20, 30, 1, 20, 30, 1],
            [30, 60, 1, 1, 20, 30, 1, 20, 30, 1, 20, 30, 1],
            [30, 60, 1, 1, 20, 30, 1, 20, 30, 1, 20, 30, 1]
        ],
        type: 'heatmap',
        colorscale: 'Viridis'
    }];
    
    data[0]['z'].forEach((row, i) => {
        row.forEach((cell, j) => {
            annotations.push({
                x: j,
                y: i,
                xref: 'x',
                yref: 'y',
                text: `${i}${j}`,
                showarrow: false,
                font: {
                    color: 'white'
                }
            });
        });
    });

    const layout = {
        title: 'Hole Cards Performance',
        annotations: annotations,
        plot_bgcolor: "#2c2c2c",
        paper_bgcolor: "#2c2c2c",
        font: {
            color: "#ccc"
        },
        xaxis: {
            tickvals: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
            ticktext: number,
            side: 'top',
            gridcolor: "#444"

        },
        yaxis: {
            tickvals:  [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
            ticktext: number,
            autorange: 'reversed',
            gridcolor: "#444",
        }
    };

    Plotly.newPlot('hole-cards-performance-container', data, layout);
}


function plot_position_performance(start, end){
    const data = {
        "pnl": [
            3617,
            1358,
            -321,
            -2299,
            -2569
        ],
        "position": [
            "MP",
            "BTN",
            "CO",
            "BB",
            "UTG"
        ]
    };

    const trace1 = {
        x: data.position,
        y: data.pnl,
        type: 'bar',
        marker: {
            color: data.pnl.map(value => value >= 0 ? 'blue' : 'red') // Color bars based on positive/negative values
        }
    };

    const layout = {
        title: 'Position Performance',
        plot_bgcolor: "#2c2c2c",
        paper_bgcolor: "#2c2c2c",
        font: {
            color: "#ccc"
        },
        xaxis: {
            // ... (rest of your existing xaxis properties)
            gridcolor: "#444",
            title: {
                text: 'Position',
                font: {
                    color: '#ccc'
                }
            }
        },
        yaxis: {
            // ... (rest of your existing yaxis properties)
            gridcolor: "#444",
            title: {
                text: 'WinLoss',
                font: {
                    color: '#ccc'
                }
            }
        }
    };

    Plotly.newPlot('position-performance-container', [trace1], layout);
}

function show_performance_history(start, end){
    $.ajax({
        type: "GET",
        url: `/performance_history?start=${start}&end=${end}`,
        dataType: "json",
        success: function(data, status) {
            console.log(data)
            plot_performance_chart(data)
            document.querySelector('#history-performance-container p').innerText = '';
        },
    });
}


function show_hole_cards_performance(start, end){
    $.ajax({
        type: "GET",
        url: `/hole_cards_performance?start=${start}&end=${end}`,
        dataType: "json",
        success: function(data, status) {
            console.log(data)
            plot_hole_cards_performance();
            document.querySelector('#hole-cards-performance-container p').innerText = '';
        },
    });
}


function show_position_performance(start, end){
    $.ajax({
        type: "GET",
        url: `/position_performance?start=${start}&end=${end}`,
        dataType: "json",
        success: function(data, status) {
            console.log(data)
            plot_position_performance();
            document.querySelector('#position-performance-container p').innerText = '';
        },
    });
}

function ShowData(){
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    position = document.getElementById('positions').value;
        
    // Convert date strings to Date objects and get timestamps
    startTimestamp = new Date(startDate).getTime();
    endTimestamp = new Date(endDate).getTime();

    console.log('Start Date Timestamp:', startTimestamp);
    console.log('End Date Timestamp:', endTimestamp);
    console.log('Position:', position);
    
    show_history_overview(startTimestamp, endTimestamp);
    show_performance_history(startTimestamp, endTimestamp);
    show_hole_cards_performance(startTimestamp, endTimestamp);
    show_position_performance(startTimestamp, endTimestamp);
}


function ShowData(){
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    position = document.getElementById('positions').value;
            
    // Convert date strings to Date objects and get timestamps
    startTimestamp = new Date(startDate).getTime();
    endTimestamp = new Date(endDate).getTime();

    console.log('Start Date Timestamp:', startTimestamp);
    console.log('End Date Timestamp:', endTimestamp);
    console.log('Position:', position);
        
    show_history_overview(startTimestamp, endTimestamp);
    show_performance_history(startTimestamp, endTimestamp);
    show_hole_cards_performance(startTimestamp, endTimestamp);
    show_position_performance(startTimestamp, endTimestamp);
}