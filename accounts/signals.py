from .models import User, UserProfile
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver


@receiver(post_save, sender=User) # First method to connect Reciever to sender
def post_save_create_profile_reciever(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        try:
            profile = UserProfile.objects.get(User=instance)
            profile.save()
        except:
            UserProfile.objects.create(user=instance)
        

@receiver(pre_save, sender=User)
def pre_save_profile_reciever(sender, instance, **kwargs):
    pass

    
#Second Method to connect Reciever to sender
#post_save.connect(post_save_create_profile_reciever, sender=User)
