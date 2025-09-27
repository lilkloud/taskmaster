import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from sqlalchemy import func, or_

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///taskmanager.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Models
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    tasks = db.relationship('Task', backref='category_ref', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.DateTime, nullable=False)
    priority = db.Column(db.String(10), nullable=False)  # High, Medium, Low
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)

    def __repr__(self):
        return f'<Task {self.title}>'

# Create database tables
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    tasks = Task.query.order_by(Task.due_date.asc()).all()
    categories = Category.query.all()
    return render_template('index.html', tasks=tasks, categories=categories)

@app.route('/task/new', methods=['GET', 'POST'])
def new_task():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        due_date = datetime.strptime(request.form.get('due_date'), '%Y-%m-%dT%H:%M')
        priority = request.form.get('priority')
        category_id = request.form.get('category_id')
        
        task = Task(
            title=title,
            description=description,
            due_date=due_date,
            priority=priority,
            category_id=category_id if category_id != 'none' else None
        )
        
        db.session.add(task)
        db.session.commit()
        flash('Task created successfully!', 'success')
        return redirect(url_for('index'))
    
    categories = Category.query.all()
    return render_template('new_task.html', categories=categories)

@app.route('/task/<int:task_id>/edit', methods=['GET', 'POST'])
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    if request.method == 'POST':
        task.title = request.form.get('title')
        task.description = request.form.get('description')
        task.due_date = datetime.strptime(request.form.get('due_date'), '%Y-%m-%dT%H:%M')
        task.priority = request.form.get('priority')
        task.category_id = request.form.get('category_id') if request.form.get('category_id') != 'none' else None
        
        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('index'))
    
    categories = Category.query.all()
    return render_template('edit_task.html', task=task, categories=categories)

@app.route('/task/<int:task_id>/delete', methods=['POST'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/task/<int:task_id>/toggle', methods=['POST'])
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.is_completed = not task.is_completed
    db.session.commit()
    return jsonify({'success': True, 'is_completed': task.is_completed})

@app.route('/stats')
def stats():
    total_tasks = Task.query.count()
    completed_tasks = Task.query.filter_by(is_completed=True).count()
    pending_tasks = total_tasks - completed_tasks
    
    priority_stats = db.session.query(
        Task.priority,
        func.count(Task.id).label('count')
    ).group_by(Task.priority).all()
    
    category_stats = db.session.query(
        Category.name,
        func.count(Task.id).label('count')
    ).outerjoin(Task).group_by(Category.name).all()
    
    return render_template('stats.html',
                         total_tasks=total_tasks,
                         completed_tasks=completed_tasks,
                         pending_tasks=pending_tasks,
                         priority_stats=dict(priority_stats),
                         category_stats=dict(category_stats))

# API Endpoints
@app.route('/api/tasks')
def get_tasks():
    query = Task.query
    
    # Filter by completion status
    status = request.args.get('status')
    if status == 'completed':
        query = query.filter_by(is_completed=True)
    elif status == 'pending':
        query = query.filter_by(is_completed=False)
    
    # Filter by priority
    priority = request.args.get('priority')
    if priority in ['High', 'Medium', 'Low']:
        query = query.filter_by(priority=priority)
    
    # Search
    search = request.args.get('search')
    if search:
        search = f"%{search}%"
        query = query.filter(
            or_(
                Task.title.ilike(search),
                Task.description.ilike(search)
            )
        )
    
    tasks = query.order_by(Task.due_date.asc()).all()
    return jsonify([{
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'due_date': task.due_date.isoformat(),
        'priority': task.priority,
        'is_completed': task.is_completed,
        'category': task.category_ref.name if task.category_ref else None
    } for task in tasks])

if __name__ == '__main__':
    app.run(debug=True)
