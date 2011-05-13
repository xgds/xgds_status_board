class DbRouter(object):
    def db_for_read(self, model, **hints):
        if model._meta.db_table == 'StatusBoard_Announcement' or \
                model._meta.db_table == 'StatusBoard_Event' or \
                model._meta.db_table == 'StatusBoard_PlanStatus':
#            print "Select GDS Ops DB read"
            return 'gdsops'
        else:
            return None

    def db_for_write(self, model, **hints):
#        print "Class:",  model._meta.db_table
        if model._meta.db_table == 'StatusBoard_Announcement' or \
                model._meta.db_table == 'StatusBoard_Event' or \
                model._meta.db_table == 'StatusBoard_PlanStatus':
#            print "Select GDS Ops DB write"
            return 'gdsops'
        else:
            return None

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_syncdb(self, db, model):
        if db == 'gdsops':
            if model._meta.db_table == 'StatusBoard_Announcement' or \
                    model._meta.db_table == 'StatusBoard_Event' or \
                    model._meta.db_table == 'StatusBoard_PlanStatus':
                return True
            else:
                return False
        elif model._meta.db_table == 'StatusBoard_Announcement' or \
                model._meta.db_table == 'StatusBoard_Event' or \
                model._meta.db_table == 'StatusBoard_PlanStatus':
            return False
        return None
