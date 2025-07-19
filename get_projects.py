import requests

# Replace with your Toggl API token and workspace ID
TOGGL_API_TOKEN = "53b04934fa6cdd0d047ba24fea805ac0"
WORKSPACE_ID = "4443420"

def get_projects(api_token, workspace_id):
    url = f"https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/projects?active=true"
    
    try:
        response = requests.get(
            url,
            auth=(api_token, "api_token")
        )
        response.raise_for_status()
        projects = response.json()
        
        if not projects:
            print("No projects found.")
            return
        
        print("Project Name --> Project ID")
        print("=" * 40)
        for proj in projects:
            print(f"{proj.get('name')} --> {proj.get('id')}")
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching projects: {e}")

if __name__ == "__main__":
    get_projects(TOGGL_API_TOKEN, WORKSPACE_ID)


"""
Project Name --> Project ID
========================================
Growth --> 211356119
Hobbies --> 211356116
Personal --> 211356121
Relationships --> 211356114
Trash --> 212433665
Work --> 211356111
"""