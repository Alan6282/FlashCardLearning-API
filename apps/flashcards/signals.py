from django.db.models.signals import post_delete,post_save
from django.dispatch import receiver
from .models import ReviewHistory,Card,Deck
from django.core.cache import cache


@receiver([post_save,post_delete],sender=Deck)
def invalidate_product_cache(sender, instance , **kwargs):
    """
    Invalidating a Cache when a Deck is Created,Updated,Deleted
    """

    cache.delete_pattern('*deck_list*')

@receiver([post_save,post_delete],sender=Card)
def invalidate_product_cache(sender, instance , **kwargs):
    """
    Invalidating a Cache when a Deck is Created,Updated,Deleted
    """

    cache.delete_pattern('*card_list*')


@receiver([post_save,post_delete],sender=ReviewHistory)
def invalidate_product_cache(sender, instance , **kwargs):
    """
    Invalidating a Cache when a Deck is Created,Updated,Deleted
    """

    cache.delete_pattern('*review_list*')