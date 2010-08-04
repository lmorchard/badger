# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

from badger.apps.badges.models import Badge, BadgeNomination
from badger.apps.badges.models import BadgeAward, BadgeAwardee

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'BadgeAward.claimed_by'
        db.add_column('badges_badgeaward', 'claimed_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True), keep_default=False)

        awards = BadgeAward.objects.all()
        for award in awards:
            if award.awardee.user:
                award.claimed_by = award.awardee.user
                award.save()


    def backwards(self, orm):
        
        # Deleting field 'BadgeAward.claimed_by'
        db.delete_column('badges_badgeaward', 'claimed_by_id')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
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
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'badges.badge': {
            'Meta': {'unique_together': "(('title', 'slug'),)", 'object_name': 'Badge'},
            'autoapprove': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'creator_ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'main_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'only_creator_can_nominate': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'tags': ('tagging.fields.TagField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {})
        },
        'badges.badgeaward': {
            'Meta': {'object_name': 'BadgeAward'},
            'awardee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['badges.BadgeAwardee']"}),
            'badge': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['badges.Badge']"}),
            'claimed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'claimed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ignored': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'nomination': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['badges.BadgeNomination']"}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {})
        },
        'badges.badgeawardee': {
            'Meta': {'unique_together': "(('user', 'email'),)", 'object_name': 'BadgeAwardee'},
            'claim_code': ('django.db.models.fields.CharField', [], {'default': "'sf18c8i'", 'max_length': '7'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'badges.badgenomination': {
            'Meta': {'object_name': 'BadgeNomination'},
            'approved': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'approved_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'approved_why': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'badge': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['badges.Badge']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nominator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'nominator'", 'to': "orm['auth.User']"}),
            'nominee': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'nominee'", 'to': "orm['badges.BadgeAwardee']"}),
            'reason_why': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['badges']
