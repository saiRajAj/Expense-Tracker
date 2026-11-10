# import dependencies
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import sqlite3
#create object of Flask class
app = Flask(__name__)
# create database to store data
def init_db() :
    conn = sqlite3.connect('expenses.db')
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description TEXT NOT NULL,
                    category TEXT NOT NULL,
                    amount REAL NOT NULL,
                    date TEXT NOT NULL
                )""")
    conn.commit()
    conn.close()

init_db()

# show all expenses
@app.route('/')
def index():
    conn = sqlite3.connect('expenses.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM expenses ORDER BY id asc")
    expenses = cur.fetchall()
    total = sum([row[3] for row in expenses])
    conn.close()
    return render_template('index.html', expenses=expenses, total = total, title = 'All Expenses')
# add expenses
@app.route('/add', methods=['POST'])
def add():
    description = request.form['description']
    category = request.form['category']
    amount = request.form['amount']
    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if description and category and amount:
        conn = sqlite3.connect('expenses.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO expenses (description, category, amount, date) VALUES (?, ?, ?, ?)",
                    (description, category, float(amount), date))
        conn.commit()
        conn.close()
    return redirect(url_for('index'))
# delete expenses
@app.route('/delete/<int:expense_id>', methods=['POST'])
def delete(expense_id):
    conn = sqlite3.connect('expenses.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))
# filter expense
@app.route('/filter', methods = ['GET','POST'])
def filter_expense():
    conn = sqlite3.connect('expenses.db')
    cur = conn.cursor()
    filter_type = request.args.get('type')
    title = ''
    if filter_type == 'day' :
        today = datetime.now().strftime('%Y-%m-%d')
        cur.execute("SELECT * FROM expenses WHERE date(date) = ?", (today,))
        title = f'Expenses for Today {today}'
    elif filter_type == 'week' :
        current_week = datetime.now().isocalendar()[1]
        cur.execute("SELECT * FROM expenses WHERE strftime('%W', date) = ?", (current_week,))
        title = f'Expenses for Current Week {current_week}'
    elif filter_type == 'month' :
        current_month = datetime.now().strftime('%Y-%m')
        cur.execute("SELECT * FROM expenses WHERE strftime('%Y-%m', date) = ?", (current_month,))
        title = f'Expenses for Current Month {current_month}'
    elif filter_type == 'year' :
        current_year = datetime.now().strftime('%Y')
        cur.execute("SELECT * FROM expenses WHERE strftime('%Y', date) = ?", (current_year,))
        title = f'Expenses for Current Year {current_year}'
    elif filter_type == 'quarter' :
        month = datetime.now().month
        year = datetime.now().strftime('%Y')
        if month in [1, 2, 3]:
            start, end = 1, 3
            q = 'Q1'
        elif month in [4, 5, 6]:
            start, end = 4, 6
            q = 'Q2'
        elif month in [7, 8, 9]:
            start, end = 7, 9
            q = 'Q3'
        else:
            start, end = 10, 12
            q = 'Q4'
        cur.execute("""
            SELECT * FROM expenses WHERE strftime('%Y', date) = ? AND strftime('%m', date) BETWEEN ? AND ?
        """, (year, f'{start:02d}', f'{end:02d}'))
        title = f'Expenses for {q} {year}'
    elif request.method == 'POST' :
        from_date = request.form['from_date']
        to_date = request.form['to_date']
        if from_date and to_date:
            cur.execute("SELECT * FROM expenses WHERE date(date) BETWEEN ? AND ?", (from_date, to_date))
            title = f'Expenses from {from_date} to {to_date}'
        else :
            cur.execute("SELECT * FROM expenses ORDER BY id asc")
            title = 'All Expenses'
    else :
        cur.execute("SELECT * FROM expenses ORDER BY id asc")
        title = 'All Expenses'
    expenses = cur.fetchall()
    total = sum([row[3] for row in expenses])
    conn.close()
    return render_template('index.html', expenses=expenses, total = total, title = title)
# visualization of expenses
@app.route('/chart-data')
def chart_data():
    conn = sqlite3.connect('expenses.db')
    cur = conn.cursor()
    cur.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    category_data = cur.fetchall()
    conn.close()
    labels = [row[0] for row in category_data]
    values = [row[1] for row in category_data]
    return jsonify(labels=labels, values=values)
# run the app
if __name__ == '__main__':
    init_db()
    app.run(debug=True)