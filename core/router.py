class ConfigDatabaseRouter:
    """
    A router to control all database operations on models in the config_database application.
    """

    def db_for_read(self, model, **hints):
        """
        Attempts to read config_database models go to config_database database.
        """
        if model._meta.app_label == 'user_data':
            return 'user_data'

        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write config_database models go to config_database database.
        """
        if model._meta.app_label == 'user_data':
            return 'user_data'

        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the config_database app is involved.
        """
        if obj1._meta.app_label == 'user_data' or obj2._meta.app_label == 'user_data':
            return True

        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the config_database app only appears in the 'config_database' database.
        """
        if app_label == 'user_data':
            return db == 'user_data'

        return None

# Register the router in Django settings
