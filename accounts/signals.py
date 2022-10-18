from .models import User, UserProfile
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver


@receiver(post_save, sender=User) 
def post_save_create_profile_reciever(sender, instance, created, **kwargs):
    if created:
        user=instance
        profile= UserProfile.objects.create(user=user)
        profile.save()
    else:
        try: 
            user=instance
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.save()
        except:
            #create userprofile if not exist
            user=instance
            profile= UserProfile.objects.create(user=user)
            profile.save()

        
@receiver(pre_save, sender=User)
def pre_save_profile_reciever(sender, instance, **kwargs):
    pass

    
#Second Method to connect Reciever to sender
#post_save.connect(post_save_create_profile_reciever, sender=User)
