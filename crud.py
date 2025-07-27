from sqlalchemy.orm import Session
from models import Expense
from datetime import datetime

# Get all expenses (sorted newest first)
def get_expenses(db: Session):
    return db.query(Expense).order_by(Expense.date.desc()).all()

# Create a new expense
def create_expense(db: Session, description: str, category: str, amount: float):
    expense = Expense(description=description, category=category, amount=amount)
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense

# Get a single expense by ID
def get_expense(db: Session, expense_id: int):
    return db.query(Expense).filter(Expense.id == expense_id).first()

# Update an existing expense
def update_expense(db: Session, expense_id: int, description: str, category: str, amount: float):
    expense = get_expense(db, expense_id)
    if expense:
        expense.description = description
        expense.category = category
        expense.amount = amount
        db.commit()
        db.refresh(expense)
    return expense

# Delete an expense
def delete_expense(db: Session, expense_id: int):
    expense = get_expense(db, expense_id)
    if expense:
        db.delete(expense)
        db.commit()
