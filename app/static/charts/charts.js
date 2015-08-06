
function plot_beer_on_draft(beer, beer_data)
{
    $('#chart').highcharts({
        chart: {
            type: 'spline'
        },
        title: {
            text: 'Days on Draft'
        },

        xAxis: {
            type: 'datetime',
            title: {
                text: 'Date'
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