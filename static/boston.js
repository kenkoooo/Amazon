$(document).ready(function () {

    $.when(
        $.getJSON("/status")
    ).done(function (status) {
        status.forEach(function (item) {
            var status = "";
            if (item["status"] == "done") {
                status = "<a href='/csv/" + item["key"] + "' target='_blank'><span class='label label-success'>Download</span></a>";
            } else if (item["status"] == "pending") {
                status = '<span class="label label-info">Pending</span>';
            } else if (item["status"] == "error") {
                status = '<span class="label label-danger">Error</span>';
            } else if (item["status"] == "running") {
                status = '<span class="label label-warning">Running</span>';
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

