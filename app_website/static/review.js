let startTimestamp;
let endTimestamp;
let position;

function getCookie(name) {
    var value = "; " + document.cookie;
    var parts = value.split("; " + name + "=");
    if (parts.length == 2) return parts.pop().split(";").shift();
}

function show_history_overview(start, end) {
    $.ajax({
        type: "GET",
        url: `/hand_history_overview?start=${start}&end=${end}`,
        dataType: "html",
        headers: {
            "Authorization": "Bearer " + getCookie('jwt')
        },
        success: function(data, status) {
            console.log(data)
            $("#table-container").html(data);
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.error(textStatus, errorThrown);
        }
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


function plot_hole_cards_performance(pnl_dict){
    const number = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
    let annotations =  []
    let pnl_array = [[], [], [], [], [], [], [], [], [], [], [], [], []]
    const data = [
        {
            z: pnl_array,
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
                text = `${number[j]}${number[i]}s`
            }else if(i<j){
                text = `${number[i]}${number[j]}o`
            }

            pnl_array[j][i] = pnl_dict[text] ? pnl_dict[text] : NaN;

            annotations.push({
                x: i,
                y: j,
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
        headers: {
            "Authorization": "Bearer " + getCookie('jwt') // Assuming JWT is stored in a cookie named 'jwt'
        },
        success: function(data, status) {
            console.log(data)
            plot_performance_chart(data)
            document.querySelector('#history-performance-container p').innerText = '';
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.error(textStatus, errorThrown); // Optional: Add error handling here
        }
    });
}


function show_hole_cards_performance(start, end){
    $.ajax({
        type: "GET",
        url: `/hole_cards_performance?start=${start}&end=${end}`,
        dataType: "json",
        headers: {
            "Authorization": "Bearer " + getCookie('jwt') // Assuming JWT is stored in a cookie named 'jwt'
        },
        success: function(data, status) {
            console.log(data)
            plot_hole_cards_performance(data);
            document.querySelector('#hole-cards-performance-container p').innerText = '';
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.error(textStatus, errorThrown); // Optional: Add error handling here
        }
    });
}


function show_position_performance(start, end){
    $.ajax({
        type: "GET",
        url: `/position_performance?start=${start}&end=${end}`,
        dataType: "json",
        headers: {
            "Authorization": "Bearer " + getCookie('jwt') // Assuming JWT is stored in a cookie named 'jwt'
        },
        success: function(data, status) {
            console.log(data)
            plot_position_performance(data);
            document.querySelector('#position-performance-container p').innerText = '';
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.error(textStatus, errorThrown); // Optional: Add error handling here
        }
    });
}


function ShowData(){
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    // const position = document.getElementById('positions').value;
    // const username = document.getElementById('usernameDisplay').textContent;
        
    // Convert date strings to Date objects and get timestamps
    startTimestamp = new Date(startDate).getTime();
    endTimestamp = new Date(endDate).getTime();

    console.log('Start Date Timestamp:', startTimestamp);
    console.log('End Date Timestamp:', endTimestamp);
    // console.log('Position:', position);
    // console.log('Username:', username);
    
    show_history_overview(startTimestamp, endTimestamp);
    show_performance_history(startTimestamp, endTimestamp);
    show_hole_cards_performance(startTimestamp, endTimestamp);
    show_position_performance(startTimestamp, endTimestamp);
}

function logout() {
    console.log('Logged out');
    document.getElementById('usernameDisplay').textContent = '';
    document.getElementById('logoutButton').style.display = 'none';
    $(".auth-buttons").show();
    document.cookie = "jwt=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    location.reload(); 
}