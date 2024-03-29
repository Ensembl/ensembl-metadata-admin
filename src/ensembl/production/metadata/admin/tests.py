#   See the NOTICE file distributed with this work for additional information
#   regarding copyright ownership.
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#       http://www.apache.org/licenses/LICENSE-2.0
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.from django.apps import AppConfig
from django.test import TestCase
from rest_framework.test import APIClient, APITestCase
from rest_framework.reverse import reverse
from rest_framework import status
from django.contrib.auth.models import User

from ensembl.production.metadata.admin.models import Dataset, Attribute, DatasetAttribute, DatasetSource, Organism, \
    Assembly, Genome


class GenomeViewSetTestCase(APITestCase):
    fixtures = ['three_assemblies.json']

    def setUp(self):
        self.client = APIClient()

    def test_genome_viewset_get(self):
        response = self.client.get(reverse('ensembl_metadata:genome-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(reverse('ensembl_metadata:genome-list'))
        self.assertIsNotNone(response.data)

    def test_genome_viewset_get_individual(self):
        genome_uuid = 'bacf0d6d-9de0-4467-865b-e5099cb45e88'
        response = self.client.get(reverse('ensembl_metadata:genome-detail', args=[genome_uuid]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data)


class CascadeDeleteTestCase(TestCase):
    def setUp(self):
        self.organism = Organism.objects.create(
            taxonomy_id=12345,
            common_name='Test Organism',
            biosample_id='test_organism',
            scientific_name='Testus organismus',
        )

        self.assembly = Assembly.objects.create(
            accession='Test Accession',
            level='Test Level',
            name='Test Name',
        )

        self.genome = Genome.objects.create(
            organism=self.organism,
            assembly=self.assembly,
            production_name='Test Production Name',
        )

    def test_cascade_delete_organism(self):
        self.organism.delete()

        with self.assertRaises(Genome.DoesNotExist):
            Genome.objects.get(pk=self.genome.pk)

    def test_cascade_delete_assembly(self):
        self.assembly.delete()

        with self.assertRaises(Genome.DoesNotExist):
            Genome.objects.get(pk=self.genome.pk)


class DatasetViewSetTestCase(APITestCase):
    fixtures = ['three_assemblies.json']

    def setUp(self):
        # self.client = APIClient()
        self.user = User.objects.create_user(username='test_user', password='test', is_superuser=True, is_staff=True)
        self.client.login(username='test_user', password='test')

    def test_dataset_viewset_get(self):
        response = self.client.get(reverse('ensembl_metadata:dataset-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data)

    def test_dataset_viewset_get_individual(self):
        dataset_uuid = '8ce01799-dabe-4d0f-b0ad-1bbd95d59f8e'
        response = self.client.get(reverse('ensembl_metadata:dataset-detail', args=[dataset_uuid]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data)

    def test_dataset_create_no_genome(self):
        payload = {
            'user': 'test_user',
            'genome_uuid': 'eeb53722-0e6d-4970-972f-c840989e0ef6',
            "name": "Test Dataset",
            "description": "This is a test dataset.",
            "label": "This is a test.",
            "dataset_type": "variation",
            "dataset_source": {
                "name": "homo_sapiens_core_108_38",
                "type": "core"
            },
            "dataset_attribute": [
                {
                    "value": "Test Value 1",
                    "name": "total_exons"
                },
                {
                    "value": "Test Value 2",
                    "name": "total_genes"
                }]
        }

        response = self.client.post(reverse('ensembl_metadata:dataset-list'), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_dataset_create_success(self):
        payload = {
            'user': 'test_user',
            'genome_uuid': 'bacf0d6d-9de0-4467-865b-e5099cb45e88',
            "name": "Test Dataset",
            "description": "This is a test dataset.",
            "label": "This is a test.",
            "dataset_type": "variation",
            "dataset_source": {
                "name": "homo_sapiens_core_108_38",
                "type": "core"
            },
            "dataset_attribute": [
                {
                    "value": "Test Value 1",
                    "name": "total_exons"
                },
                {
                    "value": "Test Value 2",
                    "name": "New_Attribute"
                }]
        }
        response = self.client.post(reverse('ensembl_metadata:dataset-list'), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Check that the data has been properly added.
        dataset = Dataset.objects.get(name=payload['name'])
        self.assertEqual(dataset.name, payload['name'])
        self.assertEqual(dataset.label, payload['label'])
        for attribute_data in payload['dataset_attribute']:
            attribute_obj = Attribute.objects.get(name=attribute_data['name'])
            dataset_attribute = DatasetAttribute.objects.get(
                dataset=dataset,
                attribute=attribute_obj,
                value=attribute_data['value']
            )
            self.assertIsNotNone(dataset_attribute)

        try:
            dataset_source = DatasetSource.objects.get(name=payload['dataset_source']['name'])
        except DatasetSource.DoesNotExist:
            self.fail("DatasetSource was not created or retrieved correctly")

    def test_dataset_delete_success(self):
        payload = {
            'user': 'test_user',
            'genome_uuid': 'bacf0d6d-9de0-4467-865b-e5099cb45e88',
            "name": "Test Dataset",
            "description": "This is a test dataset.",
            "label": "This is a test.",
            "dataset_type": "variation",
            "dataset_source": {
                "name": "homo_sapiens_core_108_38",
                "type": "core"
            },
            "dataset_attribute": [
                {
                    "value": "Test Value 1",
                    "name": "total_exons"
                },
                {
                    "value": "Test Value 2",
                    "name": "New_Attribute"
                }]
        }

        create_response = self.client.post(reverse('ensembl_metadata:dataset-list'), payload, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        dataset_uuid = create_response.data['dataset_uuid']
        delete_response = self.client.delete(reverse('ensembl_metadata:dataset-detail', args=[dataset_uuid]))
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

        get_response = self.client.get(reverse('ensembl_metadata:dataset-detail', args=[dataset_uuid]))
        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_dataset_update_no_dataset(self):
        payload = {
            "user": "danielp",
            "dataset_uuid": "553ff922-39db-40de-9f82-91b72ad577ea",
            "dataset_attribute": [
                {
                    "value": "Test Value 1",
                    "name": "total_exons"
                },
                {
                    "value": "Test Value 2",
                    "name": "total_genes"
                }
            ]
        }

        response = self.client.put(
            reverse('ensembl_metadata:dataset-detail', kwargs={'dataset_uuid': payload['dataset_uuid']}), payload,
            format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_dataset_update_success(self):
        payload = {
            "user": "danielp",
            "dataset_uuid": "8ce01799-dabe-4d0f-b0ad-1bbd95d59f8e",
            "dataset_attribute": [
                {
                    "value": "Test Value 1",
                    "name": "total_exons"
                },
                {
                    "value": "Test Value 2",
                    "name": "total_genes"
                }
            ]
        }
        response = self.client.put(
            reverse('ensembl_metadata:dataset-detail', kwargs={'dataset_uuid': payload['dataset_uuid']}), payload,
            format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        dataset = Dataset.objects.get(dataset_uuid=payload['dataset_uuid'])
        for attribute_data in payload['dataset_attribute']:
            attribute_obj = Attribute.objects.get(name=attribute_data['name'])
            dataset_attribute = DatasetAttribute.objects.get(
                dataset=dataset,
                attribute=attribute_obj,
                value=attribute_data['value']
            )
            self.assertIsNotNone(dataset_attribute)
