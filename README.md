# Step-by-Step Guide for Syncing Toggl Time Entries and Apple Calendar

[中文](README.zh.md)

This guide provides clear, sequential instructions for setting up and using the scripts to interact with Toggl and calendar data.

## Prerequisites
- Ensure you have **Python 3** installed on your **Macbook**.
- Have a **Toggl account** with access to your API token and workspace ID.
- Have a **calendar application** (Apple Calendar Only) where you can create calendars.

## Step-by-Step Setup

### 1. Clone the Repository
Download or clone the repository to your local machine and navigate to the project directory:
```bash
cd toggl-to-calendar
```

### 2. Install Dependencies
Check if a `requirements.txt` file exists in the project directory. If it does, install the required Python packages:
```bash
pip install -r requirements.txt
```
If there is no `requirements.txt`, install any necessary packages manually as mentioned in the script comments or documentation.

### 3. Set Up the Configuration File
The scripts require a `config.json` file with your Toggl credentials and project mappings.

#### a. Create `config.json`
If `config.json` does not exist in the project directory, create it manually.

#### b. Add Configuration Details
Copy the following template into `config.json` and fill in your credentials:
```json
{
  "TOGGL_API_TOKEN": "YOUR_TOGGL_API_TOKEN_HERE",
  "TOGGL_WORKSPACE_ID": "YOUR_WORKSPACE_ID_HERE",
  "id_to_name": {
    "000000001": "Work",
    "000000002": "Personal",
    "000000003": "Growth",
    "000000004": "Relationships",
    "000000005": "Hobbies"
  }
}
```
- **TOGGL_API_TOKEN**: Log in to Toggl, go to **Profile > Profile Settings > API Token**, and click "Reveal" to copy your token.
- **TOGGL_WORKSPACE_ID**: In Toggl, navigate to your projects. The workspace ID is the string of numbers in the URL.
- **id_to_name**: Map Toggl project IDs to names (e.g., "Work", "Personal"). To find project IDs, proceed to Step 4.

**Security Note**: Keep `config.json` secure and do not share it publicly.

### 4. Fetch Toggl Project IDs
To populate the `id_to_name` section of `config.json`, run the following command to retrieve your Toggl project IDs and names:
```bash
python get_projects.py
```
Update the `id_to_name` section in `config.json` with the project IDs and corresponding names displayed by the script.

### 5. Create Calendars in Your Calendar Application
Before running `sync.py`, create calendars in your calendar application (e.g., Google Calendar, Outlook) with names that **exactly match** the project names listed in the `id_to_name` section of `config.json`. For example, if `id_to_name` includes `"Work"` and `"Personal"`, create calendars named "Work" and "Personal".

### 6. Run the Scripts
- To fetch Toggl project data:
  ```bash
  python get_projects.py
  ```
- To execute the main functionality (e.g., syncing Toggl data with calendars):
  ```bash
  python sync.py
  ```

## Important Notes
- Ensure you have the necessary permissions and valid API tokens for Toggl and your calendar provider.
- Verify that your calendar names match the `id_to_name` entries exactly, as the scripts rely on these names to function correctly.
- Refer to comments within the scripts (`get_projects.py`, `sync.py`) for additional details or troubleshooting.
- If you encounter issues, double-check your `config.json` for accuracy and ensure all dependencies are installed.

By following these steps in order, you should be able to set up and use the scripts successfully.