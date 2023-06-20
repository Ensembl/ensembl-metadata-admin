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
    fixtures = ['nine_assemblies.json']  # Assuming you have a fixture named 'your_fixture.json'

    def setUp(self):
        self.client = APIClient()

    def test_genome_viewset_get(self):
        response = self.client.get(reverse('ensembl_metadata:genome-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data)

    def test_genome_viewset_get_individual(self):
        genome_uuid = 'a7335667-93e7-11ec-a39d-005056b38ce3'
        response = self.client.get(reverse('ensembl_metadata:genome-detail', args=[genome_uuid]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data)


class DatasetViewSetTestCase(APITestCase):
    fixtures = ['nine_assemblies.json']

    def setUp(self):
        # self.client = APIClient()
        self.user = User.objects.create_user(username='test_user', password='test', is_superuser=True, is_staff=True)
        self.client.login(username='test_user', password='test')

    def test_dataset_viewset_get(self):
        response = self.client.get(reverse('ensembl_metadata:dataset-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data)

    def test_dataset_viewset_get_individual(self):
        dataset_uuid = '559d7660-d92d-47e1-924e-e741151c2cef'
        response = self.client.get(reverse('ensembl_metadata:dataset-detail', args=[dataset_uuid]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data)

    def test_dataset_create_no_genome(self):
        payload = {
            'user': 'testuser',
            'genome_uuid': 'a7335667-9999-11ec-a39d-005056b38ce3',
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
            'user': 'testuser',
            'genome_uuid': 'a7335667-93e7-11ec-a39d-005056b38ce3',
            "name": "Test Dataset",
            "description": "This is a test dataset.",
            "label": "This is a test.",
            "dataset_type": "variation",
            "dataset_source": "homo_sapiens_core_108_38"
        }

        response = self.client.post(reverse('ensembl_metadata:dataset-list'), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_dataset_viewset_delete(self):
        dataset_uuid = 'c98064f7-9861-4797-9999-30ad1567d816'
        response = self.client.delete(reverse('ensembl_metadata:dataset-detail', args=[dataset_uuid]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)