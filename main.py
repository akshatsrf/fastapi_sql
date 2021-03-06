from fastapi import FastAPI,Depends,status, Response
import schemas,models
from sqlalchemy.orm import Session
from database import engine,SessionLocal
from celery import Celery

app = FastAPI()

models.Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get('/')
def func():
    return "Add /docs in the URL for Swagger UI"

@app.post('/blog', status_code=status.HTTP_201_CREATED)
def create(blog: schemas.Blog, db: Session = Depends(get_db)):
    new_blog  = models.Blog(title = blog.title, body = blog.body)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog

@app.get('/blog')
def all( db: Session = Depends(get_db)):
    blogs = db.query(models.Blog).all()
    return blogs

@app.delete('/blog/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_blog(id, db: Session = Depends(get_db)):
    db.query(models.Blog).filter(models.Blog.id == id).delete(synchronize_session=False)
    db.commit()
    return 'blog deleted'


@app.get('/blog/{id}', status_code=status.HTTP_200_OK)
def specific(id: int,response: Response, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'detail' : f'Blog with the id {id} is not available'}
    return blog
