from ensembl_metadata_registry.settings.base import *  # @UnusedWildImport
from django.test.runner import DiscoverRunner


class UnManagedModelTestRunner(DiscoverRunner):
    '''
    Test runner that automatically makes all unmanaged models in your Django
    project managed for the duration of the test run.
    Many thanks to the Caktus Group: http://bit.ly/1N8TcHW
    '''

    def setup_test_environment(self, *args, **kwargs):
        from django.apps import apps
        self.unmanaged_models = [m for m in apps.get_models() if not m._meta.managed]
        for m in self.unmanaged_models:
            m._meta.managed = True

        super(UnManagedModelTestRunner, self).setup_test_environment(*args, **kwargs)

    def teardown_test_environment(self, *args, **kwargs):
        super(UnManagedModelTestRunner, self).teardown_test_environment(*args, **kwargs)
        # reset unmanaged models
        for m in self.unmanaged_models:
            m._meta.managed = False

DATABASE_ROUTERS = []
#
# # Skip the migrations by setting "MIGRATION_MODULES"
# # to the DisableMigrations class defined above
# #
# MIGRATION_MODULES = DisableMigrations()


MIGRATION_MODULES = {
    'assembly': None,
    'compara': None,
    'datarelease': None,
    'division': None,
    'genomeinfo': None,
    'ncbi_taxonomy': None,
    'organism': None,
    'variation': None

}


# Set Django's test runner to the custom class defined above
TEST_RUNNER = 'ensembl_metadata_registry.settings.test.UnManagedModelTestRunner'
