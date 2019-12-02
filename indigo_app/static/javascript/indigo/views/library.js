(function(exports) {
  "use strict";

  if (!exports.Indigo) exports.Indigo = {};
  Indigo = exports.Indigo;

  // List of works for a place
  Indigo.PlaceDetailView = Backbone.View.extend({
    el: '#library',
    events: {
      'click .list-group-item a': 'linkClicked',
      'shown.bs.collapse .work-extra-detail': 'workDetailToggled',
      'hidden.bs.collapse .work-extra-detail': 'workDetailToggled',
    },

    initialize: function() {
      this.drawCharts();
    },

    drawCharts: function() {
      this.drawActivityChart();
      this.drawWorksByTypeChart();
      this.drawCompletenessChart();
    },

    linkClicked: function(e) {
      // don't bubble to avoid collapsing the container unnecessarily
      e.stopPropagation();
    },

    workDetailToggled: function(e) {
      var row = e.target.parentNode,
          $icon = $(row).find('.collapse-indicator'),
          opened = $(e.target).hasClass('show');

      $icon.toggleClass('fa-caret-right', !opened)
           .toggleClass('fa-caret-down', opened);
    },

    drawCompletenessChart: function() {
        var canvas = document.getElementById('completeness-chart'),
            ctx = canvas.getContext('2d'),
            data = _.map(canvas.getAttribute('data-values').split(','), function(i) { return parseInt(i); });

        new Chart(ctx, {
          type: 'line',
          data: {
            labels: data,
            datasets: [{
              label: 'Completeness',
              data: data,
              backgroundColor: 'rgba(67, 159, 120, 0.2)',
              borderColor: 'rgba(67, 159, 120, 1)',
              borderWidth: 2,
              fill: 'start',
            }]
          },
          options: {
            maintainAspectRatio: false,
            tooltips: {
              callbacks: {
                title: function(items, data) { return items[0].value + '%'; },
                label: function(item, data) { return; },
                beforeLabel: function(item, data) { return; },
              },
            },
            layout: {
              padding: {
                top: 2,
                left: 2,
                right: 2,
                bottom: 1,
              }
            },
            legend: {display: false},
            elements: {
              line: {
                tension: 0.4,
              },
              point: {
                radius: 0,
              },
            },
            scales: {
              xAxes: [{display: false}],
              yAxes: [{
                display: false,
                ticks: {
                  min: 0,
                  max: 100,
                  beginAtZero: true,
                }
              }]
            }
          }
        });
    },

    drawActivityChart: function() {
      var canvas = document.getElementById('activity-chart'),
          ctx = canvas.getContext('2d'),
          data = JSON.parse(canvas.getAttribute('data-values'));

      data = _.map(data, function(pair) { return {t: pair[0], y: pair[1]}; });

      new Chart(ctx, {
        type: 'bar',
        data: {
          labels: data,
          datasets: [{
            label: "Actions",
            data: data,
            borderWidth: 0,
            backgroundColor: 'rgba(67, 159, 120, 1)',
          }]
        },
        options: {
          maintainAspectRatio: false,
          legend: {display: false},
          scales: {
            xAxes: [{
              type: 'time',
              distribution: 'linear',
              time: {
                minUnit: 'day',
              },
              ticks: {
                source: 'auto',
                autoSkip: true,
              }
            }],
            yAxes: [{
              display: true,
              ticks: {
                min: 0,
                beginAtZero: true,
              },
            }],
          }
        }
      });
    },

    drawWorksByTypeChart: function() {
      var canvas = document.getElementById('works_by_type-chart'),
          ctx = canvas.getContext('2d'),
          data = JSON.parse(canvas.getAttribute('data-values'));

      var values = _.map(data, function(pair) { return pair[1]; });
      var labels = _.map(data, function(pair) { return pair[0]; });

      new Chart(ctx, {
        type: 'horizontalBar',
        data: {
          labels: labels,
          datasets: [{
            data: values,
            borderWidth: 0,
            backgroundColor: 'rgba(67, 159, 120, 1)',
          }]
        },
        options: {
          maintainAspectRatio: false,
          legend: {display: false},
          scales: {
            yAxes: [{
              ticks: {
                precision: 0,
                beginAtZero: true,
              },
            }],
          },
        }
      });
    },
  });
})(window);
