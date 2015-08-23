(function(exports) {
  "use strict";

  if (!exports.Indigo) exports.Indigo = {};
  Indigo = exports.Indigo;

  /**
   * Handle the document analysis view.
   */
  Indigo.DocumentAnalysisView = Backbone.View.extend({
    el: '.document-analysis-view',
    termsTemplate: '#terms-template',
    events: {
      'click .link-definitions': 'linkDefinitions',
    },

    initialize: function(options) {
      this.termsTemplate = Handlebars.compile($(this.termsTemplate).html());
      this.model.on('change', this.render, this);
    },

    render: function() {
      var terms = this.findTerms();

      this.$el.find('.document-terms-list').html(this.termsTemplate({terms: terms}));
    },

    /** Find defined terms in this document */
    findTerms: function() {
      return _.map(this.model.xmlDocument.querySelectorAll('meta TLCTerm'), function(elem) {
        return elem.getAttribute('showAs');
      }).sort();
    },

    linkDefinitions: function(e) {
      var self = this,
          $btn = this.$el.find('.link-definitions'),
          data = {
            document: {
              content: this.model.toXml()
            }
          };

      $btn.prop('disabled', true);

      $.ajax({
        url: '/api/analysis/link-terms',
        type: "POST",
        data: JSON.stringify(data),
        contentType: "application/json; charset=utf-8",
        dataType: "json"})
        .then(function(response) {
          self.model.setXml(response.document.content);
        })
        .always(function() {
          $btn.prop('disabled', false);
        });
    },
  });
})(window);
