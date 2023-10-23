let mistake
let note

function getCookie(name) {
    var value = "; " + document.cookie;
    var parts = value.split("; " + name + "=");
    if (parts.length == 2) return parts.pop().split(";").shift();
}

function show_history_details(id) {
    $.ajax({
        type: "GET",
        url: `/hand_history_details?game_id=${id}`,
        dataType: "json",
        headers: {
            "Authorization": "Bearer " + getCookie('jwt')
        },
        success: function(data, status) {
            console.log(data)
            mistake = data.is_diagnose
            note = data.note
            $("#table-container").html(data.table_html);
            document.getElementById("cards").innerHTML = `My Cards: &nbsp;&nbsp; ${data.my_cards} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Table Cards: &nbsp;&nbsp; ${data.table_cards}`;
            document.getElementById("cards").style.color = "#ccc";  // Change to your desired color

        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.error(textStatus, errorThrown);
        }
    });
}

function highlightFirstRow() {
    $('#diagnoseButton').addClass('clicked');

    if (mistake){
        $('#diagnoseButton').addClass('mistake');
        // document.getElementById("note").innerHTML = note;
        $('table tr td:nth-child(10)').show();
        $('table tr th:nth-child(10)').show();
    }else{
        $('#diagnoseButton').addClass('no-mistake');
        // document.getElementById("note").innerHTML = 'No mistakes detected.';
    }

    $('table tr').each(function(){
        const diagnose = $(this).find('td:last').html();
        if(diagnose == 'False') {
            $(this).addClass('highlight');
        }
    });
}
