from django.db import models

# Create your models here.

class Address(models.Model):
    network = models.CharField(max_length=15)
    last_updated = models.DateTimeField(auto_now_add=True)
 
    def save(self, *args, **kwargs):
        self.__class__.objects.exclude(id=self.id).delete()
        super(Address, self).save(*args, **kwargs)
    
    @classmethod
    def load(cls):
        """
        Load object from the database. Failing that, create a new empty
        (default) instance of the object and return it (without saving it
        to the database).
        """
        try:
            return cls.objects.get()
        except cls.DoesNotExist:
            return cls()

class Emotion(models.Model):
    """
      Emotion       Lights	    Web Text	
    1 Fear	        255.255.0	225.183.0	
    2 Joviality	    0.255.0	    7.185.24	
    3 Serenity	    0.255.255	49.133.156	
    4 Sadness	    0.0.255	    33.55.94	
    5 Fatigue	    255.0.255	149.55.53	
    6 Hostility	    255.0.0	    255.0.0	    
    7 Guilt	        255.128.0	224.107.10	
    """
    label = models.CharField(max_length=32)
    color = models.CharField(max_length=16)
    html_color = models.CharField(max_length=8)
    
class Topic(models.Model):
    topic = models.CharField(max_length=255)
    mood = models.ForeignKey(Emotion)
    created_at = models.DateTimeField(auto_now_add=True)

class Result(models.Model):
    search_term = models.CharField(max_length=255)
    topics = models.ManyToManyField(Topic)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        get_latest_by = 'created_at'
        ordering = ['-created_at']

class TwitterTopic(models.Model):
    topic = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        get_latest_by = 'created_at'
        ordering = ['-created_at']