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
            color: '#52BE80',
            size: 10
        },
        line: {
            color: '#52BE80',
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
            color: '#EC7063',
            size: 10
        },
        line: {
            color: '#EC7063',
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
    let pnl_dict= {
        "44": -3467,
        "53o": 1886,
        "72o": 2590,
        "76s": -4036,
        "82o": 2526,
        "A7o": -2963,
        "AA": 3354,
        "K7o": -137,
        "KAo": -1061,
        "Q2o": 3617,
        "QKo": 6290,
        "T4o": -2890,
        "TKo": -752,
        "TQo": 5452
    }
    const data = [
        {
            z: [[-1473, -51, 2087, 1857, 2894, 2579, -119, 1550, 1752, -718, -2681, 2226, -2249], [2792, -2418, -2289, -2933, 1986, -2649, -2374, -65, -2190, 225, 2416, -2973, 2023], [726, -908, -1218, -2991, -1192, -2367, -2864, -2831, 155, -759, 2295, 1951, 2387], [-267, -1725, -2461, -2445, 2266, 2510, 1415, -2684, -516, -2695, 265, -1703, 1546], [-395, -2139, 2653, 1112, 264, 2343, 2664, -1339, 805, 263, -2260, -1128, -2066], [1174, -2579, -2151, -2002, -2710, -1091, -2822, -1474, -426, 2233, 942, -1184, 1559], [236, -2722, 1196, 1995, -874, -2105, 2012, 2106, 532, 2054, -508, 2554, -1890], [-211, -1853, 2097, 929, -2473, -2740, -2997, 1503, -1857, -1753, -326, 900, 1788], [1766, -128, -2203, 146, -2732, 1442, -2769, 2499, 2986, 2630, 25, 1599, 2029], [2779, 428, -560, 2864, 2099, 1197, -2595, 2234, -1627, -2441, 566, 669, 2699], [2920, -303, -2173, 2833, 2581, -1000, 1366, -981, -1124, 63, 636, 280, -1005], [-2615, 446, 1376, 658, 1615, -2326, 302, -1904, -2201, -2359, -771, -1588, -2900], [1809, -2864, 1053, -818, 1833, 570, -1976, -1727, 2394, 72, -131, 1078, -1781]],
            type: 'heatmap',
            colorscale: 'Viridis',
            colorbar: {
                title: {
                    text: 'PnL', // The title of the color bar
                    side: 'top' // Specify the side where the title should be displayed
                },
                titleside: 'right',
                titlefont: {
                    size: 14,
                    color: '#ccc'
                }
            }
        }
    ];
    

    for (let i=0; i<number.length; i++){
        for (let j=0; j<number.length; j++){
            if (i===j){
                text = `${number[i]}${number[j]}`
            }else if(i>j){
                text = `${number[i]}${number[j]}o`
            }else if(i<j){
                text = `${number[i]}${number[j]}s`
            }
            annotations.push({
                x: j,
                y: i,
                xref: 'x',
                yref: 'y',
                text: text,
                showarrow: false,
                font: {
                    color: 'white'
                }
            });

        }
    }

    console.log(annotations)
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


function plot_position_performance(raw){
    const data = {
        "pnl": raw['pnl'],
        "position": raw['position']
    };

    const trace1 = {
        x: data.position,
        y: data.pnl,
        type: 'bar',
        marker: {
            color: data.pnl.map(value => value >= 0 ? '#5DADE2' : '#DC7633') // Color bars based on positive/negative values
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
            plot_position_performance(data);
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