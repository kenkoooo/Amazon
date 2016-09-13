$(document).ready(function () {

    $.when(
        $.getJSON("/status")
    ).done(function (status) {
        status.forEach(function (item) {
            var status = "";
            if (item["status"] == "done") {
                status = "<a href='/csv/" + item["key"] + "' target='_blank'>Download</a>";
            } else {
                status = item["status"];
            }


            var tr = '<tr>' +
                '<th scope="row">' + item["key"] + '</th>' +
                '<td>' + status + '</td>' +
                '<td>' + item["date"] + '</td>' +
                '</tr>';
            $("#status-table").append(tr);
        });
    }).fail(function () {
        console.log("error");
    });

    $("#push-button").click(function () {
        var node = $("#node-id").val();
        var num = $("#push-num").val();
        $.get("/push/" + node + "/" + num);
    });
});

