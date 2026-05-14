from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.contrib.auth import get_user_model
from .models import Wallet, Transaction
from .serializers import TransferSerializer
from typing import Any, cast

User = get_user_model()

class SendMoneyView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = TransferSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Use cast to tell Pylance the type after is_valid() check
        validated_data = cast(dict[str, Any], serializer.validated_data)
        
        sender = request.user
        receiver_id = validated_data['receiver_id']
        amount = validated_data['amount']

        # Rest of your code...
        if sender.id == receiver_id:
            return Response(
                {"error": "Cannot transfer money to yourself"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            receiver = User.objects.get(id=receiver_id)
        except User.DoesNotExist:
            return Response(
                {"error": "Receiver not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            with transaction.atomic():
                sender_wallet = Wallet.objects.select_for_update().get(user=sender)
                receiver_wallet = Wallet.objects.select_for_update().get(user=receiver)

                if sender_wallet.balance < amount:
                    return Response(
                        {"error": "Insufficient balance"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                sender_wallet.balance -= amount
                receiver_wallet.balance += amount

                sender_wallet.save()
                receiver_wallet.save()

                Transaction.objects.create(
                    sender=sender,
                    receiver=receiver,
                    amount=amount,
                    status="SUCCESS"
                )

            return Response(
                {"message": "Transfer successful"},
                status=status.HTTP_201_CREATED
            )

        except Wallet.DoesNotExist:
            return Response(
                {"error": "Wallet not found for user"},
                status=status.HTTP_404_NOT_FOUND
            )
