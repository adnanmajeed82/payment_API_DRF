from rest_framework import serializers
from .models import Transaction

class TransferSerializer(serializers.Serializer):
    receiver_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)