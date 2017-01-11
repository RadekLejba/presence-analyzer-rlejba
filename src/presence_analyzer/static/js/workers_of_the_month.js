google.load("visualization", "1", {packages:["corechart"], 'language': 'en'});
(function($) {
    $(document).ready(function(){

        var $loading = $('#loading');

        $.getJSON("/api/v1/months", function(result) {
            var $dropdown = $("#user-id");

            $.each(result, function(item) {
               $dropdown.append($('<option />', {
                'value': this.month,
                'text': this.date 
                }));
            });

            $dropdown.show();
            $loading.hide();

        });
        $('#user-id').change(function(){
            var selected_month = $("#user-id option:selected").text(),
                $chart_div = $('#chart-div'),
                $avatar = $("#avatar");

            if(selected_month) {

                $loading.show();
                $chart_div.hide();
                $avatar.hide();

                $.getJSON("/api/v1/workers_of_the_month/"+selected_month, function(result) {
                    if(result!=0){
                        var chart = new google.visualization.ColumnChart($chart_div[0]),
                            options = {};

                        var data = google.visualization.arrayToDataTable([
                            ['User', 'Time', { role: 'style' } ],
                            [result[0][0], result[0][1], 'color: #334D5C;'],
                            [result[1][0], result[1][1], 'color: #45B29D;'],
                            [result[2][0], result[2][1], 'color: #EFC94C;'],
                            [result[3][0], result[3][1], 'color: #E27A3F;'],
                            [result[4][0], result[4][1], 'color: #DF5A49;']
                        ]);
                        $chart_div.show();
                        chart.draw(data, options);
                    }else{
                        $chart_div.show();
                        $chart_div.text("No data for this month.");
                    }
                    $loading.hide();

                });
            }    
        });
    });
})(jQuery);
