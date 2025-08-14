from abc import ABC, abstractmethod
from typing import Dict, Any
import json
import requests
from deprecated import deprecated

# Type alias for configuration
Config = Dict[str, Any]

class Assistant(ABC):
    def __init__(self):
        self.api_key = None
        self.base_url = None
    
    def initialize(self, cfg: Config):
        try: 
            self.api_key = cfg["AGENT_API_KEY"]
            self.base_url = cfg.get("AGENT_URL", "https://api.openai.com/v1")
        except KeyError as e:
            raise e

    @abstractmethod
    def query(self, prompt: str) -> str:
        pass

    @staticmethod
    def build_assistant(cfg: Config) -> 'Assistant':
        # For now, return a default LLM assistant
        # You can extend this to support different assistant types
        assistant = LLMAssistant()
        assistant.initialize(cfg)
        return assistant


class LLMAssistant(Assistant):
    def query(self, prompt: str) -> str:
        """Send a query to the LLM API using requests"""
        if not self.api_key or not self.base_url:
            raise ValueError("Assistant not properly initialized")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-3.5-turbo",  # Default model, can be configurable
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {e}")
        except (KeyError, IndexError) as e:
            raise Exception(f"Invalid API response format: {e}")


class ReportAnalyzer: 
    def __init__(self, cfg_path: str):
        # we will use an LLM model to evaluate the report
        self.cfg_path = cfg_path

    def _load_config(self):
        """Load configuration from file or environment"""
        try:
            with open(self.cfg_path, 'r') as f:
                self.cfg: Config = json.load(f)
        except FileNotFoundError:
            # Fallback to environment variables or default values
            import os
            self.cfg: Config = {
                "AGENT_API_KEY": os.getenv("AGENT_API_KEY", "your-api-key-here"),
                "AGENT_URL": os.getenv("AGENT_URL", "https://api.openai.com/v1")
            }

    def _load_agent(self):
        """Initialize the LLM agent"""
        if not hasattr(self, "cfg"):
            self._load_config()
        
        self.agent = Assistant.build_assistant(self.cfg)

    def _build_prompt(self, report: str, report_type: str = "DAILY"):
        return self._build_prompt_v2(report, report_type)
    
    @deprecated(reason="Use _build_prompt_v2 instead")
    def _build_prompt_v1(self, report: str, report_type: str = "DAILY") -> str:
        tmp = "Today" if report_type == "DAILY" else "This week"
        return f"""
        Please analyze the following {report_type.lower()} calendar and time tracking summary. Your job is to simulate a fast, focused evening performance review that helps the user understand:

        1. Whether they followed their plan
        2. If they were overworking, underworking, or in balance
        3. What reminders need cleanup or rescheduling
        4. General patterns and tactical recommendations

        ---

        📋 Calendar Summary:
        {report}

        ---

        🧭 Plan vs. Reality
        - Did the user follow their plan? Answer Yes / Partially / No.
        - Did they overwork, slack off, or work at a sustainable pace?

        🔍 Reminders Check
        - Highlight completed vs. overdue reminders.
        - Comment on the backlog status: Clean / Manageable / Needs triage.

        ⚖️ Judgment Summary Table
        
        | Aspect        | Status       | Comment                              |
        |---------------|--------------|--------------------------------------|
        | Execution     | ✅/⚠️/✖️        | e.g., “Solid & goal-aligned”         |
        | Effort        | ✅/⚠️/✖️        | e.g., “Sustainable deep work”        |
        | Planning      | ✅/⚠️/✖️        | e.g., “No structure → drift risk”    |
        | Wellbeing     | ✅/⚠️/✖️        | e.g., “No evidence of physical care” |

        🧠 One-Line Debrief (optional)
        - "{tmp} felt ______ because ______."

        🎯 Tactical Recommendations
        - Provide 1–3 practical tips for improving scheduling, workload balance, or clarity tomorrow.
        """

    def _build_prompt_v2(self, report: str, report_type: str = "DAILY") -> str:
        tmp = "Today" if report_type.upper() == "DAILY" else "This week"
        return f"""
        Please analyze the following {report_type.lower()} calendar and time tracking summary. Your job is to simulate a fast, focused evening performance review and fill in the given template. 
        ---

        ⚡ {tmp} Quick Performance Review Template
        
        📋 Calendar & Time Tracking Summary:
        {report}

        ---

        ### 1️⃣ {tmp} Execution Overview

        | Category    | Planned | Completed | Completion Rate | Status | Notes / Keywords |
        |-----------|--------|----------|----------------|--------|----------------|
        | Tasks      | —      | —        | —              | —      | —              |
        | Reminders  | —      | —        | —              | —      | —              |

        ### 2️⃣ Workload & Pace

        | Metric                 | {tmp} Data   | Ideal Range | Status | Notes |
        |-----------------------|--------------|------------|--------|-------|
        | Deep Work Hours        | —            | 3–5h       | —      | —     |
        | Shallow / Fragmented   | —            | ≤2h        | —      | —     |
        | Total Work Hours       | —            | 5–7h       | —      | —     |
        | Rest / Sleep           | (Sleep is usually not recorded, you may infer from the data.)  | 7–8h       | —      | —     |

        

        ### 3️⃣ Reminders / Backlog Quick Check
        
        - ✅ Completed: —
        - ⚠️ Overdue: — → Prioritize first thing tomorrow
        
        > Comment on the backlog status: Clean / Manageable / Needs triage.

        ### 4️⃣ Tactical Recommendations (Next Day)

        1. e.g. Handle overdue reminders → Prioritize 9–10 AM tomorrow
        2. e.g. Deep work → Reserve a continuous 2h block, no fragmentation
        3. e.g. Plan calibration → Quickly confirm top 3 key tasks for {tmp} in the morning

        ### 5️⃣ One-Line Self-Debrief

        > "{tmp} completion rate —, deep work —, ⚠️ backlog — → Handle overdue first thing tomorrow, keep deep work blocks uninterrupted."
        
        ### 6️⃣ Motivation / Positive Feedback

        > e.g. "Great effort today! Keep building momentum — small consistent steps compound into big results."
        
        """
    
    def generate_analysis(self, report: str, report_type: str = "DAILY") -> str:
        """Generate analysis of the calendar report using LLM"""
        if not hasattr(self, "cfg"):
            self._load_config()
        if not hasattr(self, "agent"):
            self._load_agent()

        prompt = self._build_prompt(report, report_type)
        
        try:
            analysis = self.agent.query(prompt)
            return analysis
        except Exception as e:
            return f"Error generating analysis: {str(e)}"


def debug():

    # Initialize components
    analyzer = ReportAnalyzer("config.json")  # Added missing config path

    try:
        # Generate calendar summary
        summary = """
        🗓️ Comprehensive Daily Summary for 2025-07-30

        📅 Planned Calendar Events:
        (none)

        ⏱️ Actual Events (Toggl):
        13:57:00–15:09:00 | MIT Manipulation Course | Growth | Note: Imported from Toggl - ID: cb76b354...
        09:55:00–11:57:00 | LeetCode | Growth | Note: Imported from Toggl - ID: ecf45304...

        🚨 Overdue Reminders:
        🔴 HKU Position | Personal | Due: Wednesday, July 30, 2025 00:00:00

        ✅ Completed Reminders:
        ✓ Leetcode | Growth
        ✓ MIT Manipulation Course | Growth

        📊 Summary:
        Calendar Events: 0 planned, 3 actual (Toggl)
        Reminders: 6 total (3 overdue, 3 completed)
        """

        # Analyze the summary
        result = analyzer.generate_analysis(summary)  # Fixed: pass summary as argument
        
        print(result)
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    debug()