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
from rest_framework.test import APIClient, APITestCase
from rest_framework.reverse import reverse
from rest_framework import status
from django.contrib.auth.models import User


class GenomeViewSetTestCase(APITestCase):
    fixtures = ['three_assemblies.json']

    def setUp(self):
        self.client = APIClient()

    def test_genome_viewset_get(self):
        response = self.client.get(reverse('ensembl_metadata:genome-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data)

    def test_genome_viewset_get_individual(self):
        genome_uuid = '553ff910-39db-40de-9f82-91b72ad577ea'
        response = self.client.get(reverse('ensembl_metadata:genome-detail', args=[genome_uuid]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data)


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
        dataset_uuid = '2b2469a3-94f8-4c68-9211-7677126d9579'
        response = self.client.get(reverse('ensembl_metadata:dataset-detail', args=[dataset_uuid]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data)

    def test_dataset_create_no_genome(self):
        payload = {
            'user': 'test_user',
            'genome_uuid': 'eeb537c0-0e6d-4970-972f-c840989e0ef6',
            "name": "Test Dataset",
            "description": "This is a test dataset.",
            "label": "This is a test.",
            "dataset_type": "variation",
            "dataset_source": "homo_sapiens_core_108_38"
        }

        response = self.client.post(reverse('ensembl_metadata:dataset-list'), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_dataset_create_success(self):
        payload = {
            'user': 'test_user',
            'genome_uuid': 'eeb537c0-0e6d-4970-972f-c840989e0ef6',
            "name": "Test Dataset",
            "description": "This is a test dataset.",
            "label": "This is a test.",
            "dataset_type": "variation",
            "dataset_source": "homo_sapiens_core_110_38"
        }

        response = self.client.post(reverse('ensembl_metadata:dataset-list'), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_dataset_delete_success(self):
        # first create a dataset to delete
        payload = {
            'user': 'test_user',
            'genome_uuid': 'eeb537c0-0e6d-4970-972f-c840989e0ef6',
            "name": "Test Dataset for deletion",
            "description": "This is a test dataset for deletion.",
            "label": "This is a test for deletion.",
            "dataset_type": "variation",
            "dataset_source": "homo_sapiens_core_110_38"
        }

        create_response = self.client.post(reverse('ensembl_metadata:dataset-list'), payload, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        dataset_uuid = create_response.data['dataset_uuid']
        delete_response = self.client.delete(reverse('ensembl_metadata:dataset-detail', args=[dataset_uuid]))
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

        get_response = self.client.get(reverse('ensembl_metadata:dataset-detail', args=[dataset_uuid]))
        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)
