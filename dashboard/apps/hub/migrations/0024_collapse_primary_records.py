# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        # NON-SPECIAL PRIMARIES
        # Group non-special primary elections by state and end_date
        groups = {}
        for elec in orm['hub.Election'].objects.filter(special=False, race_type='primary'):
            key = (elec.state_id, elec.end_date)
            groups.setdefault(key, []).append(elec)

        # Collapse multiple primaries on same date into a single record,
        # making sure to merge office metadata
        for key, elecs in sorted(groups.items()):
            if len(elecs) > 1:
                print "%s has %s elections to merge" % (key, len(elecs))
                to_keep = elecs[0]
                # Merge office fields into target and delete the record
                for elec in elecs[1:]:
                    print "Merging %s with %s" % (elec, to_keep)
                    for office in ('prez', 'senate', 'house', 'gov', 'state_officers', 'state_leg'):
                        if getattr(elec, office) == True:
                            setattr(to_keep, office, True)
                    elec.delete()
                    print "Deleted: %s" % elec
                to_keep.save()
                print "Saved merged record: %s" % to_keep
            else:
                pass

        # Special primaries should be grouped by state, end_date, office and district
        # We simply need to delete any redundant ones. No need to merge since
        # these are always for a single race.
        specials = {}
        for elec in orm['hub.Election'].objects.filter(special=True, race_type='primary'):
            if not elec.end_date:
                raise Exception("%s has no end_date" % elec)
            key = (elec.state_id, elec.end_date, elec.office_id, elec.district)
            specials.setdefault(key, []).append(elec)

        print "Consolidating special primaries..."
        for key, elecs in specials.items():
            if len(elecs) > 1:
                to_keep = elecs[0]
                for elec in elecs[1:]:
                    print "Deleted %s" % elec
                    elec.delete()
                print "Kept %s" % to_keep


    def backwards(self, orm):
        "Write your backwards methods here."

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'hub.contact': {
            'Meta': {'ordering': "['last_name']", 'object_name': 'Contact'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '254', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '70'}),
            'middle_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'mobile': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'blank': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'org': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hub.Organization']"}),
            'phone': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '70', 'blank': 'True'})
        },
        'hub.dataformat': {
            'Meta': {'ordering': "['name']", 'object_name': 'DataFormat'},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'primary_key': 'True'})
        },
        'hub.election': {
            'Meta': {'ordering': "['state', '-end_date']", 'object_name': 'Election'},
            'absentee_and_provisional': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'cong_dist_level': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'county_level': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'direct_link': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'district': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '5', 'db_index': 'True', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {'db_index': 'True', 'blank': 'True'}),
            'formats': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['hub.DataFormat']", 'symmetrical': 'False'}),
            'gov': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'house': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level_note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'office': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hub.Office']", 'null': 'True', 'blank': 'True'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hub.Organization']", 'null': 'True'}),
            'portal_link': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'precinct_level': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'prez': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'primary_type': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10', 'db_index': 'True', 'blank': 'True'}),
            'race_type': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_index': 'True'}),
            'result_type': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'senate': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'special': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hub.State']"}),
            'state_leg': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'state_leg_level': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'state_level': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'state_officers': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'hub.log': {
            'Meta': {'ordering': "['-date']", 'object_name': 'Log'},
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hub.Contact']", 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'follow_up': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'formal_request': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'gdoc_link': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'org': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hub.Organization']", 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hub.State']"}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'hub.office': {
            'Meta': {'ordering': "['name']", 'object_name': 'Office'},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'primary_key': 'True'})
        },
        'hub.organization': {
            'Meta': {'ordering': "['name']", 'object_name': 'Organization'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '75', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'fec_page': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'gov_agency': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'gov_level': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '150'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'db_index': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '75', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        'hub.state': {
            'Meta': {'ordering': "['name']", 'object_name': 'State'},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'postal': ('django.db.models.fields.CharField', [], {'max_length': '2', 'primary_key': 'True'})
        },
        'hub.volunteer': {
            'Meta': {'ordering': "['last_name']", 'object_name': 'Volunteer'},
            'affil': ('django.db.models.fields.CharField', [], {'max_length': '254', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '254', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '70'}),
            'middle_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'mobile': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'blank': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'phone': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'blank': 'True'}),
            'roles': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['hub.VolunteerRole']", 'symmetrical': 'False'}),
            'skype': ('django.db.models.fields.CharField', [], {'max_length': '254', 'blank': 'True'}),
            'states': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['hub.State']", 'symmetrical': 'False', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '70', 'blank': 'True'}),
            'twitter': ('django.db.models.fields.CharField', [], {'max_length': '254', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'website': ('django.db.models.fields.CharField', [], {'max_length': '254', 'blank': 'True'})
        },
        'hub.volunteerlog': {
            'Meta': {'object_name': 'VolunteerLog'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'follow_up': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'gdoc_link': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'volunteer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hub.Volunteer']"})
        },
        'hub.volunteerrole': {
            'Meta': {'object_name': 'VolunteerRole'},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '30', 'primary_key': 'True'})
        }
    }

    complete_apps = ['hub']
    symmetrical = True
