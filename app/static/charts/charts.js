


function plot_beer_on_draft(beer, beer_data) {


    $('#chart').highcharts({
        chart: {
            type: 'spline'
        },
        title: {
            text: 'On Draft (Last 30 Days)'
        },

        xAxis: {
            type: 'datetime',
            title: {
                text: 'Date'
            },
            dateTimeLabelFormats: {
                day: '%b %e'
            }
        },
        yAxis: {
            title: {
                text: 'Draft'
            },
            min: 0,
            max: 1,
            allowDecimals: false,
            categories: ['Off','On']
        },

        tooltip: {
                xDateFormat: ' %A, %b %e'
        },

        plotOptions: {
            spline: {
                marker: {
                    enabled: true
                }
            }



        },

        series: [{
            name: beer,
            data: beer_data

        }]

    });
  }