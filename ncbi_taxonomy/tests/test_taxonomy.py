from rest_framework.test import APITestCase
from ncbi_taxonomy.models import TaxonomyName, TaxonomyNode
from ncbi_taxonomy.api.utils import TaxonomyUtils


class TaxonomyTest(APITestCase):
    databases = {'ncbi_taxonomy'}
    fixtures = ['ncbi_taxonomy']

    def test_load_name(self):
        self.assertEquals(TaxonomyName.objects.all().count(), 355, 'Fetched all taxonomy names')
        taxonomy_names = TaxonomyName.objects.filter(taxon_id=9771, name_class='scientific name')
        taxonomy_name = taxonomy_names[0]
        self.assertEquals(taxonomy_name.name, 'Balaenoptera musculus', 'Correct scientific name')

    def test_load_node(self):
        self.assertEquals(TaxonomyNode.objects.all().count(), 125, 'Fetched all taxonomy nodes')
        taxonomy_node = TaxonomyUtils.fetch_node(436486)
        self.assertEquals(taxonomy_node.parent_id, 8492, 'Correct parent id')
        taxonomy_names = taxonomy_node.names()
        names = []
        for name in taxonomy_names:
            names.append(name.name)
        self.assertListEqual(names, ['dinosaur', 'dinosaurs'], 'Correct names')

    def test_fetch_descendant_ids(self):
        results = TaxonomyUtils.fetch_descendent_ids('9721')
        self.assertEqual(len(results), 5, 'Fetched all descendent nodes')
        expected_list = [9721, 9761, 9765, 9766, 9771]
        self.assertListEqual(expected_list, results, 'Correct descendent taxon ids')
