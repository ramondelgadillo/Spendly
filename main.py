from fastapi import FastAPI, Request, Form
from fastapi import Query
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import models

from database import Base, engine, SessionLocal
import crud

# Create the database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Mount static files (CSS, fonts, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 template directory
templates = Jinja2Templates(directory="templates")

# Dependency to get a DB session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Home Page: List all expenses
@app.get("/")
def read_home(request: Request, category: str = Query(default=None)):
    db = next(get_db())
    
    if category:
        expenses = db.query(models.Expense).filter(models.Expense.category == category).order_by(models.Expense.date.desc()).all()
    else:
        expenses = crud.get_expenses(db)
    
    total = sum(e.amount for e in expenses)

    # Spending by category
    all_expenses = crud.get_expenses(db)
    categories = {}
    for e in all_expenses:
        categories[e.category] = categories.get(e.category, 0) + e.amount

    return templates.TemplateResponse("index.html", {
        "request": request,
        "expenses": expenses,
        "total": total,
        "selected_category": category,
        "categories": categories
    })

# GET: Add Expense Page
@app.get("/add")
def add_expense_form(request: Request):
    return templates.TemplateResponse("add_expense.html", {"request": request})

# POST: Submit New Expense
@app.post("/add")
def add_expense(
    description: str = Form(...),
    category: str = Form(...),
    amount: float = Form(...)
):
    db = next(get_db())
    crud.create_expense(db, description, category, amount)
    return RedirectResponse("/", status_code=302)

# GET: Edit Expense Page
@app.get("/edit/{expense_id}")
def edit_expense_form(expense_id: int, request: Request):
    db = next(get_db())
    expense = crud.get_expense(db, expense_id)
    return templates.TemplateResponse("edit_expense.html", {
        "request": request,
        "expense": expense
    })

# POST: Submit Edited Expense
@app.post("/edit/{expense_id}")
def edit_expense(
    expense_id: int,
    description: str = Form(...),
    category: str = Form(...),
    amount: float = Form(...)
):
    db = next(get_db())
    crud.update_expense(db, expense_id, description, category, amount)
    return RedirectResponse("/", status_code=302)

# GET: Delete Expense
@app.get("/delete/{expense_id}")
def delete_expense(expense_id: int):
    db = next(get_db())
    crud.delete_expense(db, expense_id)
    return RedirectResponse("/", status_code=302)
