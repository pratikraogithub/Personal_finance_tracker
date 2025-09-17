from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Transaction, Category
from .serializers import TransactionSerializer, CategorySerializer
from django.db.models.functions import TruncMonth
from django.db.models import Sum
from collections import defaultdict
from datetime import datetime

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def category_list_create(request):
    if request.method == 'GET':
        categories = Category.objects.filter(user=request.user)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = CategorySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def transaction_list_create(request):
    if request.method == 'GET':
        transactions = Transaction.objects.filter(user=request.user).order_by('-date')
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # ✅ Fix is here
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_balance(request):
    user = request.user

    # Get all transactions for the user
    transactions = Transaction.objects.filter(user=user)

    # Calculate totals
    total_income = sum(t.amount for t in transactions if t.type == 'INCOME')
    total_expense = sum(t.amount for t in transactions if t.type == 'EXPENSE')
    balance = total_income - total_expense

    return Response({
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def monthly_summary(request):
    user = request.user
    year = request.query_params.get('year')

    # Filter transactions for the user
    transactions = Transaction.objects.filter(user=user)

    # If a year is specified, filter by year
    if year:
        try:
            year = int(year)
            transactions = transactions.filter(date__year=year)
        except ValueError:
            return Response({"error": "Invalid year format. Use YYYY."}, status=400)

    # Group by month and type
    monthly_data = transactions.annotate(month=TruncMonth('date')).values('month', 'type').annotate(total=Sum('amount')).order_by('month')

    # Format output
    from collections import defaultdict
    summary = defaultdict(lambda: {'income': 0, 'expense': 0})

    for entry in monthly_data:
        month_str = entry['month'].strftime('%Y-%m')
        if entry['type'] == 'INCOME':
            summary[month_str]['income'] = entry['total']
        elif entry['type'] == 'EXPENSE':
            summary[month_str]['expense'] = entry['total']

    result = [
        {"month": month, "income": values['income'], "expense": values['expense']}
        for month, values in sorted(summary.items())
    ]

    return Response(result)
