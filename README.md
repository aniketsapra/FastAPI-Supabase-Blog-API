# FastAPI-Supabase Blog API
A modern, secure blog backend built with FastAPI, Supabase (PostgreSQL, Auth, Storage), and Docker.
Includes features like authentication (JWT), blog post CRUD, image uploads, comments, and rate limiting.

```Features
-User authentication with SupabaseAUTH
-Create, Read, Update, Delete blog posts
-Comment on posts (rate-limited)
-Upload images to Supabase storage
-Role-based access (admin check for some routes)
-SQLAlchemy + Pydantic V2 with from_attributes=True
-Rate limiting with slowapi
```
```## Environment Variables

Create a `.env` file based on the template below:

# Supabase Config 
SUPABASE_URL=https://<your-project-id>.supabase.co
SUPABASE_KEY=sb_secret_<your-service-role-key>
SUPABASE_PROJECT_ID=<your-project-id>
SUPABASE_JWT_SECRET=<your-supabase-jwt-secret>
SUPABASE_JWKS_URL=https://<your-project-id>.supabase.co/auth/v1/.well-known/jwks.json
SUPABASE_AUDIENCE=<your-project-id>
SUPABASE_ALGORITHM=ES256

#  PostgreSQL Database 
DATABASE_URL=postgresql://<username>.<project-id>:<password>@<host>:5432/postgres

# JWT for FastAPI 
JWT_SECRET=<your-custom-jwt-secret>
```
## Docker Setup

Build & Start the Project
```docker-compose up --build```
This will:
Build the FastAPI Docker image
Start the app on 
```
http://localhost:8000
```
Test the API

Open Swagger docs:

🔗 http://localhost:8000/docs

You can also use tools like Postman or curl


```Example Routes
Method	    Endpoint	                Description
POST	    /auth/register	        Register a new user
POST	    /auth/login	            Login and get JWT token
GET         /posts	                List all posts
POST	    /post	                Create a new post (auth)
GET         /posts/{id}	            Get a single post by ID
POST	    /comments    	        Add a comment (auth)
GET         /posts/{id}/comments	Get comments (admin only)
POST	    /upload/image	        Upload image to Supabase
```

Developer Notes

    Use @limiter.limit("5/minute") to control API abuse

    Use Depends(require_admin) to protect admin routes

Technologies Used
```
    FastAPI
    Supabase
    SQLAlchemy
    Pydantic V2
    Docker
    slowapi
```
