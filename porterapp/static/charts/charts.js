


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

function plot_bac(beer_data,selector) {

    $(selector).highcharts({
        chart: {
            type: 'column'
        },
        title: {
            text: 'Alcohol consumed  in the last 4 hours'
        },

        xAxis: {

            categories:['Alcohol Consumed']

        },
        yAxis: {
            title: {
                text: 'Drunkenness ',
            },
            min: 0,
            max: 10,
            alternateGridColor:  '#FAFAFA',
            allowDecimals: false,
            categories: ['I could use a drink','Feeling Good','Slight Buzz',"I Shouldn't Drive","Work tomorrow..uh",
             "Fuck Work!","Totally Can Drive","Brain Culler" ,"?","?", "Dead"]
        },

         plotOptions: {
            column: {
                stacking: 'normal',
                dataLabels: {
                    enabled: true,
                    color: (Highcharts.theme && Highcharts.theme.dataLabelsColor) || 'white',
                    style: {
                        textShadow: '0 0 3px black'
                    }
                }
            }
        },

        tooltip: {
            pointFormat: '{series.name} :  {point.y}  <br/> Total: {point.stackTotal}'

          },

        series: beer_data



    });
  }

function plot_beer_consumed(beer_data,selector){

	$(selector).highcharts({
        chart: {
            type: 'line'
        },

        title: {
            text: 'Total Alcohol Consumed over time'
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
                text: 'oz'
            },
        },

        tooltip: {
            headerFormat: '<b>{series.name}</b><br>',
            pointFormat: '{point.x:%e. %b}: {point.y:.2f} oz'
        },

        plotOptions: {
            line: {
                marker: {
                    enabled: false,

                }
            }
        },

        series: [beer_data]
    });

}
