'''from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from finance.ai_service import query_llm
from finance.services.sql_agent import ask_sql_agent
from .models import Transaction, Category, AIInsight
from .serializers import TransactionSerializer, CategorySerializer
from django.db.models.functions import TruncMonth
from django.db.models import Sum
from collections import defaultdict
from datetime import datetime
# from .ai_service import query_llm
# import ollama



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



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def ai_finance_assistant(request):
    user = request.user
    query = request.data.get("query", "")

    # Gather user transaction summary
    transactions = Transaction.objects.filter(user=user)
    total_income = transactions.filter(type="INCOME").aggregate(Sum("amount"))["amount__sum"] or 0
    total_expense = transactions.filter(type="EXPENSE").aggregate(Sum("amount"))["amount__sum"] or 0

    summary = f"User summary:\nTotal income: ₹{total_income}\nTotal expense: ₹{total_expense}\nQuery: {query}"

    # Get AI response
    response = query_llm(summary)

    # Save insight
    AIInsight.objects.create(user=user, query=query, response=response)

    return Response({"query": query, "response": response})
'''

"""
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_query(request):
    question = request.data.get("question")

    if not question:
        return Response({"error": "No question provided"}, status=400)

    try:
        answer = ask_sql_agent(question)
        return Response({"answer": answer})

    except Exception as e:
        return Response({"error": str(e)}, status=500)
"""


from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import Category
from .serializers import CategorySerializer

from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from collections import defaultdict

from finance.models import Transaction, AIInsight
from finance.serializers import TransactionSerializer

from finance.ai_service import query_llm
from rest_framework.views import APIView



class CategoryViewSet(ModelViewSet):
    serializer_class=CategorySerializer
    permission_classes=[IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TransactionViewSet(ModelViewSet):
    serializer_class=TransactionSerializer
    permission_classes=[IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by('-date')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # /transactions/balance
    @action(detail=False, methods=['get'])
    def balance(self, request):
        qs=self.get_queryset()

        income = qs.filter(type='INCOME').aggregate(Sum('amount'))['amount__sum'] or 0
        expense = qs.filter(type='EXPENSE').aggregate(Sum('amount'))['amount__sum'] or 0

        return Response ({
            "total_income": income,
            "total_expense": expense,
            "balance": income - expense
        })
    
    @action(detail=False, methods=['get'])
    def monthly_summary(self, request):
        year = request.query_params.get('year')
        qs = self.get_queryset()

        if year:
            qs = qs.filter(date__year=int(year))

        data = qs.annotate(month=TruncMonth('date')).values('month', 'type').annotate(total=Sum('amount')).order_by('month')

        summary = defaultdict(lambda: {'income': 0, 'expense': 0})

        for row in data:
            month = row['month'].strftime('%Y-%m')
            if row['type'] == 'INCOME':
                summary[month]['income'] = row['total']
            else:
                summary[month]['expense'] = row['total']

        return Response([
            {"month": m, **v} for m, v in summary.items()
        ])
    
class AIFinanceAssistantAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        query = request.data.get("query", "")

        qs = Transaction.objects.filter(user=user)

        income = qs.filter(type='INCOME').aggregate(
            Sum('amount')
        )['amount__sum'] or 0

        expense = qs.filter(type='EXPENSE').aggregate(
            Sum('amount')
        )['amount__sum'] or 0

        prompt = (
            f"User summary:\n"
            f"Income: ₹{income}\n"
            f"Expense: ₹{expense}\n"
            f"Query: {query}"
        )

        response = query_llm(prompt)

        AIInsight.objects.create(
            user=user,
            query=query,
            response=response
        )

        return Response({
            "query": query,
            "response": response
        })
