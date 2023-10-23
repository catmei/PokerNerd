const socket = io();

socket.on('update_ui', function(data) {
    console.log(data)

    if (data['method'] === 'strategy'){
        document.getElementById('equity').innerHTML = "Equity: <br>" + data.equity;
        document.getElementById('action').innerHTML = "Action: <br>" + data.action;
        document.getElementById('amount').innerHTML = "Amount: <br>" + data.amount;
        document.getElementById('analysis').innerHTML = "Analysis: <br>" + data.analysis
    } else if(data['method'] === 'table-cards'){
        document.getElementById('table-cards').innerHTML = "Table Cards: <br>" + data['table-cards']
    } else if(data['method'] === 'my-cards'){
        document.getElementById('my-cards').innerHTML = "My Cards: <br>" + data['my-cards']
    } else if(data['method'] === 'pot'){
        document.getElementById('pot').innerHTML = "Pot: <br>" + data.pot
    } else if(data['method'] === 'clean'){
        document.getElementById('table-cards').innerHTML = "Table Cards: <br> --"
        document.getElementById('my-cards').innerHTML = "My Cards: <br> --"
        document.getElementById('pot').innerHTML = "Pot: <br> --"
        document.getElementById('equity').innerHTML = "Equity: <br> --"
        document.getElementById('action').innerHTML = "Action: <br> --"
        document.getElementById('amount').innerHTML = "Amount: <br> --"
        document.getElementById('analysis').innerHTML = "Analysis: <br> --"
    }

    // Add flash animation when content changes
    if (data['method'] !== 'clean') {
        Object.keys(data).forEach(key => {
            if (key !== 'method') {
                const element = document.getElementById(key);
                if (element) {
                    element.classList.add('flash');

                    // Remove the flash class after animation completes
                    setTimeout(() => {
                        element.classList.remove('flash');
                    }, 500);
                }
            }
        });
    }
});