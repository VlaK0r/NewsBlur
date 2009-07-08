from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from utils import feedparser, object_manager
from utils.dateutil.parser import parse as dateutil_parse
from utils.feed_functions import encode, prints, mtime
import time, datetime, random
from pprint import pprint
from django.utils.http import urlquote
from django.db.models import Q
from utils.diff import HTMLDiff

USER_AGENT = 'NewsBlur v1.0 - newsblur.com'

class Feed(models.Model):
    feed_address = models.URLField(max_length=255, verify_exists=True, unique=True)
    feed_link = models.URLField(max_length=200, blank=True)
    feed_title = models.CharField(max_length=255, blank=True)
    active = models.BooleanField(default=True)
    num_subscribers = models.IntegerField(default=0)
    last_update = models.DateTimeField(auto_now=True, default=0)
    min_to_decay = models.IntegerField(default=15)
    days_to_trim = models.IntegerField(default=90)
    creation = models.DateField(auto_now_add=True)
    etag = models.CharField(max_length=50, blank=True)
    last_modified = models.DateTimeField(null=True, blank=True)
    
    
    def __unicode__(self):
        return self.feed_title
        
    def last_updated(self):
        return time.time() - time.mktime(self.last_update.timetuple())
    
    def new_stories_since_date(self, date):
        story_count = Story.objects.filter(story_date__gte=date,
                                           story_feed=self).count()
        return story_count
        
    def add_feed(self, feed_address, feed_link, feed_title):
        print locals()
        
    def update(self, force=False, feed=None):
        if (self.last_updated() / 60) < (self.min_to_decay + (random.random()*self.min_to_decay)) and not force:
            print 'Feed unchanged: ' + self.feed_title
            return
            
        feed_updated, feed = cache.get("feed:" + self.feed_address, (None, None,))
        if feed and not force:
            print 'Feed Cached: ' + self.feed_title
        if not feed or force:
            last_modified = None
            now = datetime.datetime.now()
            if self.last_modified:
                last_modified = datetime.datetime.timetuple(self.last_modified)
            if not feed:
                print '[%d] Retrieving Feed: %s %s' % (self.id, self.feed_title, last_modified)
                feed = feedparser.parse(self.feed_address,
                                        etag=self.etag,
                                        modified=last_modified,
                                        agent=USER_AGENT)
                cache.set("feed:" + self.feed_address, (now, feed),
                          self.min_to_decay * 60 * 5)
                                
        self.last_update = datetime.datetime.now()
        
        # check for movement or disappearance
        if hasattr(feed, 'status'):
            if feed.status == 301:
                self.feed_url = feed.href
            if feed.status == 410:
                self.active = False
            if feed.status >= 400:
                return

        # Fill in optional fields
        if not self.feed_title:
            self.feed_title = feed.feed.get('title', 
                                            feed.feed.get('link', 'No Title'))
        if not self.feed_link:
            self.feed_link = feed.feed.get('link', 'null:')
            
        self.etag = feed.get('etag', '')
        if not self.etag:
            self.etag = ''

        self.last_modified = mtime(feed.get('modified', datetime.datetime.timetuple(datetime.datetime.now())))
                                 
        self.save()
        
        for story in feed['entries']:
            self.save_story(story)

        self.trim_feed();

        return

    def trim_feed(self):
        date_diff = datetime.datetime.now() - datetime.timedelta(self.days_to_trim)
        stories = Story.objects.filter(story_feed=self, story_date__lte=date_diff)
        for story in stories:
            story.story_past_trim_date = True
            story.save()
        
    def save_story(self, story):
        story = self._pre_process_story(story)

        if story.get('title'):
            story_contents = story.get('content')
            if story_contents is not None:
                story_content = story_contents[0]['value']
            else:
                story_content = story.get('summary')
            existing_story = self._exists_story(story)
            if not existing_story:
                pub_date = datetime.datetime.timetuple(story.get('published'))
                print '- New story: %s %s' % (pub_date, story.get('title'))

                s = Story(story_feed = self,
                       story_date = story.get('published'),
                       story_title = story.get('title'),
                       story_content = story_content,
                       story_author = story.get('author'),
                       story_permalink = story.get('link')
                )
                try:
                    s.save(force_insert=True)
                except:
                    pass
            elif existing_story.story_title != story.get('title') \
              or existing_story.story_content != story_content:
                # update story
                print '- Updated story in feed (%s): %s / %s' % (self.feed_title, len(existing_story.story_content), len(story_content))
                
                original_content = None
                if existing_story.story_original_content:
                    original_content = existing_story.story_original_content
                else:
                    original_content = existing_story.story_content
                diff = HTMLDiff(original_content, story_content)
                print "\t\tDiff: %s %s %s" % diff.getStats()
                # print "\t\tDiff content: %s" % diff.getDiff()
                print '\tExisting title / New: : \n\t\t- %s\n\t\t- %s' % (existing_story.story_title, story.get('title'))

                s = Story(id = existing_story.id,
                       story_feed = self,
                       story_date = story.get('published'),
                       story_title = story.get('title'),
                       story_content = diff.getDiff(),
                       story_original_content = original_content,
                       story_author = story.get('author'),
                       story_permalink = story.get('link')
                )
                try:
                    s.save(force_update=True)
                except:
                    pass
            else:
                print "Unchanged story: %s " % story.get('title')
            
        return
        
    def _exists_story(self, entry):
        pub_date = entry['published']
        start_date = pub_date - datetime.timedelta(hours=4)
        end_date = pub_date + datetime.timedelta(hours=4)
        # print "Dates: %s %s %s" % (pub_date, start_date, end_date)
        existing_story = Story.objects.filter(
            (
               Q(story_title__iexact = entry['title']) 
            ) | (
                Q(story_permalink = entry['link'])
            ), 
            Q(story_date__range=(start_date, end_date)),
            Q(story_feed = self)
        )
        if len(existing_story):
            return existing_story[0]
        else:
            return None
        
    def _pre_process_story(self, entry):
        date_published = entry.get('published', entry.get('updated'))
        if not date_published:
            date_published = str(datetime.datetime.now())
        date_published = dateutil_parse(date_published)
        # Change the date to UTC and remove timezone info since 
        # MySQL doesn't support it.
        timezone_diff = datetime.datetime.utcnow() - datetime.datetime.now()
        date_published_offset = date_published.utcoffset()
        if date_published_offset:
            date_published = (date_published - date_published_offset
                              - timezone_diff).replace(tzinfo=None)
        else:
            date_published = date_published.replace(tzinfo=None)

        entry['published'] = date_published

        protocol_index = entry['link'].find("://")
        if protocol_index != -1:
            entry['link'] = (entry['link'][:protocol_index+3]
                            + urlquote(entry['link'][protocol_index+3:]))
        else:
            entry['link'] = urlquote(entry['link'])
        return entry
            
    class Meta:
        db_table="feeds"
        ordering=["feed_title"]
        
class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name
    
    def save(self):
        super(Tag, self).save()
        
class Story(models.Model):
    '''A feed item'''
    story_feed = models.ForeignKey(Feed)
    story_date = models.DateTimeField()
    story_title = models.CharField(max_length=255)
    story_content = models.TextField(null=True, blank=True)
    story_original_content = models.TextField(null=True, blank=True)
    story_content_type = models.CharField(max_length=255, null=True,
                                          blank=True)
    story_author = models.CharField(max_length=255, null=True, blank=True)
    story_permalink = models.CharField(max_length=1000)
    story_past_trim_date = models.BooleanField(default=False)
    tags = models.ManyToManyField(Tag)

    def __unicode__(self):
        return self.story_title

    class Meta:
        verbose_name_plural = "stories"
        verbose_name = "story"
        db_table="stories"
        ordering=["-story_date", "story_feed"]
        