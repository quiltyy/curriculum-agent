## **Curriculum-Agent Notes**



**Back-End Testing:**



**# Make sure you're in your project directory**

cd "C:\\Users\\acham\\OneDrive\\Desktop\\curriculum-agent" (Desktop)



**# Activate .venv**

.\\.venv\\Scripts\\Activate.ps1



**# Run Backend Tests**

pytest -q backend/tests



**# Reinstall requirements (If Necessary)**

pip install -r requirements.txt



**# Run import\_csv.py (Runs from test\_data/test\_courses.csv**

(.venv) PS C:\\Users\\acham\\OneDrive\\Desktop\\curriculum-agent\\backend> python app/import\_csv.py





**# Enter Docker and check database**

docker exec -it curriculum-db psql -U postgres -d curriculumdb



(Alembic Upgrade Stuff if you need to review this again)



**# Check List of Relations**

\\dt



**# Run query on database** 







**#Close .venv**

deactivate







\## Include bit about "Have a more complex course schedule or major, we have specialists standing by to help you" 







🟦 Card A: GitHub repos + CI skeleton



🟩 Card B: FastAPI skeleton + Auth



🟧 Card C: DB migrations + Seed



🟨 Card D: CSV Import

