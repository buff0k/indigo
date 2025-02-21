from nose.tools import *  # noqa
from django.test import TestCase
from datetime import date

from indigo_api.models import Document, Work, Amendment, Language, Country, User
from indigo_api.tests.fixtures import *  # noqa


class DocumentTestCase(TestCase):
    fixtures = ['languages_data', 'countries', 'user', 'taxonomies', 'work', 'published']

    def setUp(self):
        self.work = Work.objects.get(id=1)
        self.eng = Language.for_code('eng')

    def test_empty_document(self):
        d = Document(work=self.work)
        self.assertIsNotNone(d.doc)

    def test_change_title(self):
        user = User.objects.get(pk=1)
        d = Document.objects.create(title="Title", frbr_uri="/akn/za/act/1980/01", work=self.work, expression_date=date(2001, 1, 1), language=self.eng, created_by_user=user, updated_by_user=user)
        d.save()
        id = d.id
        self.assertTrue(d.document_xml.startswith('<akomaNtoso'))

        d2 = Document.objects.get(id=id)
        self.assertEqual(d.title, d2.title)

    def test_set_content(self):
        d = Document()
        d.work = self.work
        d.content = document_fixture('γνωρίζω')

        assert_equal(d.frbr_uri, '/akn/za/act/1900/1')
        assert_equal(d.country, 'za')
        assert_equal(d.doc.publication_date, date(2005, 7, 24))

    def test_expression_date(self):
        d = Document(work=self.work)
        d.content = document_fixture('test')
        d.expression_date = date(2014, 1, 1)
        assert_equal(d.expression_date, date(2014, 1, 1))

    def test_empty_expression_date(self):
        d = Document(work=self.work)
        d.content = document_fixture('test')
        d.expression_date = ''
        assert_equal(d.expression_date, '')

        d.expression_date = None
        assert_equal(d.expression_date, None)

    def test_inherit_from_work(self):
        user = User.objects.get(pk=1)
        w = Work.objects.create(frbr_uri='/akn/za/act/2009/test', title='Test document', country=Country.for_code('za'), created_by_user=user)
        d = Document(work=w, expression_date='2011-02-01', language=self.eng, created_by_user=user)
        d.save()

        d = Document.objects.get(pk=d.id)
        assert_equal(w.frbr_uri, d.frbr_uri)
        assert_equal(w.title, d.title)

    def test_repeal_from_work(self):
        rep = Work.objects.get(id=2)
        d = Document.objects.get(id=1)
        w = d.work
        w.repealed_by = rep
        w.repealed_date = rep.publication_date
        w.save()

        d = Document.objects.get(id=1)
        assert_equal(d.repeal.repealing_uri, rep.frbr_uri)
        assert_equal(d.repeal.repealing_title, rep.title)
        assert_equal(d.repeal.date, rep.publication_date)

    def test_amendments_from_work(self):
        amending = Work.objects.get(id=1)
        # this work has two docs:
        #  2 - expression date: 2011-01-01
        #  3 - expression date: 2012-02-02
        amended = Work.objects.get(id=3)
        d = date(2011, 12, 10)

        # this will impact only document id 3
        user = User.objects.get(pk=1)
        a = Amendment(amending_work=amending, amended_work=amended, date=d, created_by_user=user)
        a.save()

        doc = Document.objects.get(id=2)
        # only the pre-existing amendment event
        assert_equal(len(doc.amendment_events()), 1)

        doc = Document.objects.get(id=3)
        events = list(doc.amendment_events())
        # one new in addition to the two previous ones
        assert_equal(len(events), 3)
        assert_equal(events[1].amending_uri, amending.frbr_uri)
        assert_equal(events[1].amending_title, amending.title)
        assert_equal(events[1].date, d)

    def test_get_subcomponent(self):
        d = Document(language=self.eng)
        d.work = self.work
        d.content = document_fixture(xml="""
        <body xmlns="http://docs.oasis-open.org/legaldocml/ns/akn/3.0">
          <section id="section-1">
            <num>1.</num>
            <heading>Foo</heading>
            <content>
              <p>hello</p>
            </content>
          </section>
          <chapter id="chapter-2">
            <num>2.</num>
            <heading>The Chapter</heading>
            <content>
              <p>hi</p>
            </content>
          </chapter>
        </body>
        """)

        assert_is_not_none(d.doc.components()['main'])
        elem = d.get_subcomponent('main', 'chapter/2')
        assert_equal(elem.get('id'), "chapter-2")

        elem = d.get_subcomponent('main', 'section/1')
        assert_equal(elem.get('id'), "section-1")

        assert_is_none(d.get_subcomponent('main', 'chapter/99'))
        assert_is_none(d.get_subcomponent('main', 'section/99'))

    def test_is_latest(self):
        d = Document(work=self.work)
        d.expression_date = ''
        self.assertFalse(d.is_latest())
        d.expression_date = None
        self.assertFalse(d.is_latest())
        d = Document.objects.get(id=2)
        self.assertFalse(d.is_latest())
        d = Document.objects.get(id=3)
        self.assertTrue(d.is_latest())

    def test_valid_until(self):
        d = Document(work=self.work)
        d.expression_date = ''
        self.assertIsNone(d.valid_until())
        d.expression_date = None
        self.assertIsNone(d.valid_until())
        d = Document.objects.get(id=2)
        self.assertEqual(date(2012, 2, 1), d.valid_until())
        d = Document.objects.get(id=3)
        self.assertEqual(date(2019, 1, 1), d.valid_until())

    def test_is_consolidation(self):
        d = Document(work=self.work)
        self.assertFalse(d.is_consolidation())
        d = Document.objects.get(id=2)
        self.assertFalse(d.is_consolidation())
        d = Document.objects.get(id=3)
        self.assertFalse(d.is_consolidation())
        d = Document.objects.get(id=8)
        self.assertTrue(d.is_consolidation())

    def test_consolidation_note(self):
        d = Document(work=self.work)
        self.assertEqual('A general consolidation note that applies to all consolidations in this place.', d.work.consolidation_note())
        d = Document.objects.get(id=4)
        self.assertEqual('A special consolidation note just for this work', d.work.consolidation_note())
