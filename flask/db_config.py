from flask_sqlalchemy import SQLAlchemy
from app import app

db = SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Step 2: Define the Student Model
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)       # Unique ID
    name = db.Column(db.String(100), nullable=False)   # Name cannot be blank
    status = db.Column(db.String(100), nullable=False) # Course name
    due_date = db.Column(db.DateTime(),nullable=False)                    # Grade (e.g. 'A+', 'B')

    def __repr__(self):
        return f"<Student #{self.id}: {self.name} ({self.course}) - Grade: {self.grade}>"

print("✅ Step 2 Complete: Student model defined!")

with app.app_context():
    db.create_all()