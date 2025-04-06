import os
import re
import json
import requests
import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

# Define the FastAPI app for the API endpoint
app = FastAPI(
    title="SHL Assessment Recommendation API",
    description="API for recommending SHL assessments based on job descriptions or queries",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model for API response
class AssessmentRecommendation(BaseModel):
    name: str
    url: str
    remote_testing: str
    adaptive_support: str
    duration: str
    test_type: str
    score: float

class RecommendationResponse(BaseModel):
    recommendations: List[AssessmentRecommendation]

# Load the TF-IDF vectorizer
@st.cache_resource
def get_vectorizer():
    return TfidfVectorizer(
        max_features=5000,
        stop_words='english',
        ngram_range=(1, 2)
    )

# Process the JSON data to match the expected format
def process_json_data(json_data):
    processed_data = []
    
    for item in json_data:
        # Extract the relevant fields from the new JSON format
        processed_item = {
            "name": item.get("course_name", "Unknown"),
            "url": item.get("course_url", "#"),
            # Default values for fields not in the JSON
            "remote_testing": "Yes",  # Default value
            "adaptive_support": "Yes" if any(key in ("A", "IRT") for key in item.get("keys", [])) else "No",
            "duration": "30 minutes",  # Default value
            "test_type": get_test_type(item.get("keys", [])),
            "description": f"SHL assessment: {item.get('course_name', 'Unknown')}"  # Generate a basic description
        }
        processed_data.append(processed_item)
    
    return processed_data

# Determine test type based on keys
def get_test_type(keys):
    if not isinstance(keys, list):
        return "Unknown"
    
    if "C" in keys:
        return "Cognitive"
    elif "P" in keys:
        return "Personality"
    elif "S" in keys or "T" in keys:
        return "Skill-based"
    else:
        return "Other"

# Load SHL catalog from JSON file
@st.cache_data
def get_shl_catalog():
    json_file = "shl_courses2.json"
    
    # Check if JSON file exists
    if os.path.exists(json_file):
        try:
            with open(json_file, 'r') as f:
                json_data = json.load(f)
                # Process the JSON data to match the expected format
                return process_json_data(json_data)
        except Exception as e:
            st.error(f"Error loading JSON file: {e}")
            return get_mock_data()
    
    # If file doesn't exist, use mock data
    return get_mock_data()

# Mock data in case JSON file is missing
def get_mock_data():
    return [
        {
            "name": "SHL Verify Interactive - Numerical Reasoning",
            "url": "https://www.shl.com/products/verify-interactive-numerical-reasoning/",
            "remote_testing": "Yes",
            "adaptive_support": "Yes",
            "duration": "30 minutes",
            "test_type": "Cognitive",
            "description": "Advanced numerical reasoning assessment that measures a candidate's ability to analyze and interpret numerical data. Ideal for roles requiring strong analytical skills."
        },
        {
            "name": "SHL Verify Interactive - Verbal Reasoning",
            "url": "https://www.shl.com/products/verify-interactive-verbal-reasoning/",
            "remote_testing": "Yes",
            "adaptive_support": "Yes",
            "duration": "30 minutes",
            "test_type": "Cognitive",
            "description": "Verbal reasoning assessment that evaluates a candidate's ability to understand and analyze written information. Perfect for roles requiring communication skills."
        },
        {
            "name": "Java Programming Assessment",
            "url": "https://www.shl.com/products/java-programming-assessment/",
            "remote_testing": "Yes",
            "adaptive_support": "No",
            "duration": "40 minutes",
            "test_type": "Skill-based",
            "description": "Technical assessment for Java developers that evaluates coding skills, OOP principles, and problem-solving abilities. Includes hands-on coding exercises."
        },
        {
            "name": "Python Programming Assessment",
            "url": "https://www.shl.com/products/python-programming-assessment/",
            "remote_testing": "Yes",
            "adaptive_support": "No",
            "duration": "45 minutes",
            "test_type": "Skill-based",
            "description": "Technical assessment for Python developers that evaluates data structures, algorithms, and coding skills. Includes data analysis scenarios."
        },
        {
            "name": "SQL Database Skills",
            "url": "https://www.shl.com/products/sql-database-skills/",
            "remote_testing": "Yes",
            "adaptive_support": "No",
            "duration": "35 minutes",
            "test_type": "Skill-based",
            "description": "Assessment for database professionals focusing on SQL queries, database design, and data manipulation. Evaluates practical database skills."
        },
        {
            "name": "SHL Personality Assessment (OPQ)",
            "url": "https://www.shl.com/products/product-catalog/view/occupational-personality-questionnaire/",
            "remote_testing": "Yes",
            "adaptive_support": "No",
            "duration": "25 minutes",
            "test_type": "Personality",
            "description": "Comprehensive personality assessment that measures workplace behaviors and preferences across multiple dimensions. Helps evaluate cultural fit."
        },
        {
            "name": "SHL Cognitive Assessment Package",
            "url": "https://www.shl.com/products/cognitive-assessment-package/",
            "remote_testing": "Yes",
            "adaptive_support": "Yes",
            "duration": "60 minutes",
            "test_type": "Cognitive",
            "description": "Combined package of numerical, verbal, and logical reasoning assessments to evaluate overall cognitive abilities. Comprehensive evaluation for knowledge workers."
        },
        {
            "name": "Customer Service Aptitude",
            "url": "https://www.shl.com/products/customer-service-aptitude/",
            "remote_testing": "Yes",
            "adaptive_support": "No",
            "duration": "20 minutes",
            "test_type": "Skill-based",
            "description": "Measures skills related to customer service including empathy, problem-solving, and communication. Uses situational judgment scenarios."
        },
        {
            "name": "Full-Stack Development Assessment",
            "url": "https://www.shl.com/products/full-stack-development-assessment/",
            "remote_testing": "Yes",
            "adaptive_support": "No",
            "duration": "50 minutes",
            "test_type": "Skill-based",
            "description": "Technical assessment for full-stack developers covering front-end, back-end, and database technologies. Evaluates JavaScript, HTML/CSS, and API development."
        },
        {
            "name": "ADEPT-15 Personality Questionnaire",
            "url": "https://www.shl.com/products/adept-15/",
            "remote_testing": "Yes",
            "adaptive_support": "Yes",
            "duration": "25 minutes",
            "test_type": "Personality",
            "description": "Modern personality assessment measuring 15 key workplace traits that predict job performance. Provides insights into work style and team dynamics."
        },
        {
            "name": "Data Science Assessment",
            "url": "https://www.shl.com/products/data-science-assessment/",
            "remote_testing": "Yes",
            "adaptive_support": "No",
            "duration": "45 minutes",
            "test_type": "Skill-based",
            "description": "Technical assessment for data scientists covering statistics, machine learning, and data manipulation skills. Includes Python and SQL components."
        },
        {
            "name": "SHL Verify Mechanical Reasoning",
            "url": "https://www.shl.com/products/verify-mechanical-reasoning/",
            "remote_testing": "Yes",
            "adaptive_support": "No",
            "duration": "25 minutes",
            "test_type": "Cognitive",
            "description": "Assessment measuring understanding of mechanical principles and physical concepts. Ideal for engineering and technical roles."
        },
        {
            "name": "Leadership Assessment",
            "url": "https://www.shl.com/products/leadership-assessment/",
            "remote_testing": "Yes",
            "adaptive_support": "No",
            "duration": "35 minutes",
            "test_type": "Personality",
            "description": "Evaluates leadership potential across key dimensions including strategic thinking, people management, and decision-making. Designed for management roles."
        },
        {
            "name": "JavaScript Coding Assessment",
            "url": "https://www.shl.com/products/javascript-coding-assessment/",
            "remote_testing": "Yes",
            "adaptive_support": "No",
            "duration": "40 minutes",
            "test_type": "Skill-based",
            "description": "Technical assessment for front-end developers focusing on JavaScript, DOM manipulation, and modern frameworks. Includes practical coding exercises."
        },
        {
            "name": "Business Analyst Assessment",
            "url": "https://www.shl.com/products/business-analyst-assessment/",
            "remote_testing": "Yes",
            "adaptive_support": "No",
            "duration": "45 minutes",
            "test_type": "Skill-based",
            "description": "Evaluates skills essential for business analysts including requirements gathering, process mapping, and stakeholder management."
        }
    ]

# Function to fetch JD from URL
def fetch_job_description(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract main content - adjust based on typical JD sites
        main_content = soup.find('div', class_='job-description') or soup.find('div', class_='description')
        if main_content:
            return main_content.text.strip()
        return soup.text  # Fallback to all text
    except Exception as e:
        st.error(f"Error fetching job description: {e}")
        return ""

# Function to preprocess text
def preprocess_text(text):
    # Remove special characters and extra whitespace
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip().lower()
    return text

# Function to get recommendations using TF-IDF and cosine similarity
def get_recommendations(query, catalog_data, top_k=10):
    # Preprocess query
    query = preprocess_text(query)
    
    # Prepare corpus for TF-IDF
    assessment_texts = [f"{item['name']} {item.get('description', '')}" for item in catalog_data]
    assessment_texts = [preprocess_text(text) for text in assessment_texts]
    
    # Add query to corpus for vectorization
    all_texts = assessment_texts + [query]
    
    # Create and fit vectorizer
    vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(all_texts)
    
    # Get query vector (last one in the matrix)
    query_vector = tfidf_matrix[-1]
    
    # Get assessment vectors (all except the last one)
    assessment_vectors = tfidf_matrix[:-1]
    
    # Calculate similarity
    similarities = cosine_similarity(query_vector, assessment_vectors)[0]
    
    # Get top k
    top_indices = similarities.argsort()[-top_k:][::-1]
    
    recommendations = []
    for idx in top_indices:
        item = catalog_data[idx]
        recommendations.append({
            "name": item["name"],
            "url": item["url"],
            "remote_testing": item["remote_testing"],
            "adaptive_support": item["adaptive_support"],
            "duration": item["duration"],
            "test_type": item["test_type"],
            "score": float(similarities[idx])
        })
    
    return recommendations

# Process duration constraints from query
def process_duration_constraint(query, recommendations):
    # Look for time constraints in query
    time_constraint = re.search(r'(\d+)\s*minutes', query.lower())
    
    if time_constraint:
        max_minutes = int(time_constraint.group(1))
        filtered_recommendations = []
        
        for rec in recommendations:
            # Check if duration is below constraint
            duration_text = rec['duration'].lower()
            
            # Handle ranges like "20-30 minutes"
            duration_match = re.search(r'(\d+)(?:\s*-\s*(\d+))?', duration_text)
            
            if duration_match:
                if duration_match.group(2):  # Range case
                    max_duration = int(duration_match.group(2))
                else:  # Single value case
                    max_duration = int(duration_match.group(1))
                
                if max_duration <= max_minutes:
                    filtered_recommendations.append(rec)
            else:
                # If we can't parse duration, include it anyway
                filtered_recommendations.append(rec)
        
        if filtered_recommendations:
            return filtered_recommendations
    
    return recommendations

# API endpoint for recommendations
@app.get("/api/recommend", response_model=RecommendationResponse)
async def recommend(
    query: str = Query(..., description="Job description or query text"),
    url: Optional[str] = Query(None, description="URL to extract job description from"),
    top_k: int = Query(10, description="Number of recommendations to return")
):
    catalog_data = get_shl_catalog()
    
    if url:
        job_description = fetch_job_description(url)
        if job_description:
            query = job_description
    
    recommendations = get_recommendations(query, catalog_data, top_k)
    
    # Process any duration constraints in the query
    recommendations = process_duration_constraint(query, recommendations)
    
    return {"recommendations": recommendations[:top_k]}

# Streamlit frontend
def main():
    st.set_page_config(
        page_title="SHL Assessment Recommender",
        page_icon="📋",
        layout="wide"
    )
    
    st.title("SHL Assessment Recommendation System")
    st.write("Find the right assessments for your job roles based on descriptions or queries.")
    
    # Input options
    input_method = st.radio(
        "Choose input method:",
        ("Natural Language Query", "Job Description", "URL")
    )
    
    query = ""
    
    if input_method == "Natural Language Query":
        query = st.text_area(
            "Enter your query:", 
            height=100,
            placeholder="Example: I am hiring for Java developers who can also collaborate effectively with my business teams. Looking for an assessment(s) that can be completed in 40 minutes."
        )
    
    elif input_method == "Job Description":
        query = st.text_area(
            "Paste job description:", 
            height=200,
            placeholder="Paste the complete job description here..."
        )
    
    else:  # URL
        url = st.text_input(
            "Enter Job Description URL:",
            placeholder="https://example.com/job-description"
        )
        if url:
            if st.button("Fetch Job Description"):
                with st.spinner("Fetching job description..."):
                    query = fetch_job_description(url)
                    st.text_area("Extracted Job Description", query, height=200)
    
    # Number of recommendations
    top_k = st.slider("Number of recommendations", min_value=1, max_value=10, value=5)
    
    # Process
    if st.button("Get Recommendations") and (query or (input_method == "URL" and url)):
        with st.spinner("Processing..."):
            catalog_data = get_shl_catalog()
            
            if input_method == "URL" and url and not query:
                query = fetch_job_description(url)
            
            if query:
                recommendations = get_recommendations(query, catalog_data, top_k)
                recommendations = process_duration_constraint(query, recommendations)
                
                # Display results
                st.subheader("Recommended Assessments")
                
                if recommendations:
                    df = pd.DataFrame(recommendations)
                    # Format the dataframe
                    df['Score'] = df['score'].apply(lambda x: f"{x:.2f}")
                    df = df[['name', 'url', 'remote_testing', 'adaptive_support', 'duration', 'test_type', 'Score']]
                    df.columns = ['Assessment Name', 'URL', 'Remote Testing', 'Adaptive/IRT Support', 'Duration', 'Test Type', 'Match Score']
                    
                    # Convert URLs to clickable links
                    df['URL'] = df['URL'].apply(lambda x: f'<a href="{x}" target="_blank">Link</a>')
                    
                    st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)
                else:
                    st.warning("No matching assessments found. Try modifying your query.")
            else:
                st.error("Please provide a query or job description.")
    
    # API documentation
    with st.expander("API Documentation"):
        st.markdown("""
        ## API Endpoint
        
        You can access the recommendation system programmatically using our API:
        
        **Endpoint:** `GET /api/recommend`
        
        **Parameters:**
        - `query` (required): Job description or query text
        - `url` (optional): URL to extract job description from
        - `top_k` (optional): Number of recommendations to return (default: 10)
        
        **Example Request:**
        ```
        GET /api/recommend?query=Java developers with collaboration skills&top_k=5
        ```
        
        **Example Response:**
        ```json
        {
            "recommendations": [
                {
                    "name": "Java Programming Assessment",
                    "url": "https://www.shl.com/...",
                    "remote_testing": "Yes",
                    "adaptive_support": "Yes",
                    "duration": "30 minutes",
                    "test_type": "Skill-based",
                    "score": 0.95
                },
                ...
            ]
        }
        ```
        """)

# Entry point to run FastAPI with Uvicorn when deployed as API
def start_api():
    uvicorn.run("app:app", host="0.0.0.0", port=8000)

if __name__ == "__main__":
    # For Streamlit
    main()