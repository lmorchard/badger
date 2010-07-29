# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Badge'
        db.create_table('badges_badge', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50, db_index=True)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('tags', self.gf('tagging.fields.TagField')()),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('creator_ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15, null=True, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('badges', ['Badge'])

        # Adding model 'BadgeAwardee'
        db.create_table('badges_badgeawardee', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True)),
        ))
        db.send_create_signal('badges', ['BadgeAwardee'])

        # Adding model 'BadgeNomination'
        db.create_table('badges_badgenomination', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('badge', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['badges.Badge'])),
            ('nominee', self.gf('django.db.models.fields.related.ForeignKey')(related_name='nominee', to=orm['badges.BadgeAwardee'])),
            ('nominator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='nominator', to=orm['auth.User'])),
            ('approved', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('reason_why', self.gf('django.db.models.fields.TextField')()),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('badges', ['BadgeNomination'])

        # Adding model 'BadgeAward'
        db.create_table('badges_badgeaward', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('badge', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['badges.Badge'])),
            ('nomination', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['badges.BadgeNomination'])),
            ('awardee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['badges.BadgeAwardee'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('badges', ['BadgeAward'])

        notification = models.get_app('notification')

        notification.create_notice_type(
            "badge_nomination_sent", 
            _("Badge Nomination Sent"), 
            _("you have sent a nomination for a badge")
        )

        notification.create_notice_type(
            "badge_nomination_received", 
            _("Badge Nomination Received"), 
            _("you have been nominated for a badge")
        )

        notification.create_notice_type(
            "badge_nomination_proposed", 
            _("Badge Nomination Proposed"), 
            _("someone has been nominated to receive a badge for which you are a decision maker")
        )

        notification.create_notice_type(
            "badge_nomination_rejected", 
            _("Badge Nomination Rejected"), 
            _("a decision maker for a badge has rejected a nomination for award")
        )

        notification.create_notice_type(
            "badge_awarded", 
            _("Badge Awarded"), 
            _("a badge has been awarded")
        )

        notification.create_notice_type(
            "badge_award_claimed", 
            _("Badge Award Claimed"), 
            _("a badge award has been claimed")
        )

        notification.create_notice_type(
            "badge_award_rejected", 
            _("Badge Award Rejected"), 
            _("a badge award has been rejected")
        )

        notification.create_notice_type(
            "badge_award_ignored", 
            _("Badge Award Ignored"), 
            _("a badge award has been ignored")
        )

    def backwards(self, orm):
        
        # Deleting model 'Badge'
        db.delete_table('badges_badge')

        # Deleting model 'BadgeAwardee'
        db.delete_table('badges_badgeawardee')

        # Deleting model 'BadgeNomination'
        db.delete_table('badges_badgenomination')

        # Deleting model 'BadgeAward'
        db.delete_table('badges_badgeaward')


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
            'Meta': {'object_name': 'Badge'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'creator_ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'tags': ('tagging.fields.TagField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {})
        },
        'badges.badgeaward': {
            'Meta': {'object_name': 'BadgeAward'},
            'awardee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['badges.BadgeAwardee']"}),
            'badge': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['badges.Badge']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nomination': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['badges.BadgeNomination']"}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {})
        },
        'badges.badgeawardee': {
            'Meta': {'object_name': 'BadgeAwardee'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'})
        },
        'badges.badgenomination': {
            'Meta': {'object_name': 'BadgeNomination'},
            'approved': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'badge': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['badges.Badge']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nominator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'nominator'", 'to': "orm['auth.User']"}),
            'nominee': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'nominee'", 'to': "orm['badges.BadgeAwardee']"}),
            'reason_why': ('django.db.models.fields.TextField', [], {}),
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
