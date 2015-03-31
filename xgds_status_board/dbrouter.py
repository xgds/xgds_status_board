# __BEGIN_LICENSE__
#Copyright (c) 2015, United States Government, as represented by the 
#Administrator of the National Aeronautics and Space Administration. 
#All rights reserved.
#
#The xGDS platform is licensed under the Apache License, Version 2.0 
#(the "License"); you may not use this file except in compliance with the License. 
#You may obtain a copy of the License at 
#http://www.apache.org/licenses/LICENSE-2.0.
#
#Unless required by applicable law or agreed to in writing, software distributed 
#under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR 
#CONDITIONS OF ANY KIND, either express or implied. See the License for the 
#specific language governing permissions and limitations under the License.
# __END_LICENSE__

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
