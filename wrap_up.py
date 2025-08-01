import os
from typing import Optional, Literal
from datetime import datetime, timedelta
from summarize_calendar import CalendarSummarizer
from ai_summary import ReportAnalyzer
from sync import sync 

def wrap_up(option: Optional[Literal["DAILY", "WEEKLY"]] = "DAILY", do_sync: Optional[bool] = False) -> None:
    """Generate and analyze calendar reports for Daily or Weekly periods"""
    
    today = datetime.now()
    
    if do_sync:
        sync()

    # Calculate date range based on option
    if option.upper() == "DAILY":
        if today.hour < 6: 
            start_date = today - timedelta(1)
        else: 
            start_date = today

        end_date = today
        date_str = start_date.strftime("%Y-%m-%d")
        report_type = "DAILY"
    elif option.upper() == "WEEKLY":
        # Get start of current week (Monday)
        days_since_monday = today.weekday()
        start_date = today - timedelta(days=days_since_monday)
        end_date = start_date + timedelta(days=6)
        date_str = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        report_type = "WEEKLY"
    else:
        raise ValueError(f"Unsupported option: {option}")

    # Initialize components
    summarizer = CalendarSummarizer()

    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    analyzer = ReportAnalyzer(config_path)

    try:
        # Generate calendar summary based on the option
        if option == "DAILY":
            summary = summarizer.generate_summary(start_date.strftime("%Y-%m-%d"))
        else:  # Weekly
            # Assuming CalendarSummarizer can handle date ranges
            summary = summarizer.generate_summary(
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d")
            )
        
        # Analyze the summary with context about the report type
        result = analyzer.generate_analysis(summary, report_type=option)

        outputLines = []
        
        outputLines.append("=" * 60)
        outputLines.append(f"📊 CALENDAR ANALYSIS REPORT - {report_type}")
        outputLines.append(f"📅 Period: {date_str}")
        outputLines.append(f"⏰ Generated: {today.strftime('%Y-%m-%d %H:%M:%S')}")
        outputLines.append("\n" + "=" * 20 + " 📝 SUMMARY " + "=" * 20)
        outputLines.append(summary)
        outputLines.append("\n" + "=" * 20 + " 🔍 ANALYSIS " + "=" * 19)
        outputLines.append(result)
        outputLines.append("=" * 60)
        
        # Join all lines and print the complete report
        return "\n".join(outputLines)
        
    except Exception as e:
        print(f"Error generating {option.lower()} report: {e}")

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Generate calendar analysis reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
        Examples:
        python script.py --daily     Generate daily report
        python script.py --weekly    Generate weekly report
        python script.py            Generate daily report (default)
                """
            )
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--daily", 
        action="store_true",
        help="Generate daily calendar analysis report"
    )
    group.add_argument(
        "--weekly", 
        action="store_true", 
        help="Generate weekly calendar analysis report"
    )

    parser.add_argument(
        "--sync",
        action="store_true",
        help="Sync from toggl to apple calendar"
    )

    parser.add_argument(
        "--save",
        action="store_true",
        help="Save report to file"
    )
    
    return parser.parse_args()

if __name__ == "__main__":
    import argparse
    args = parse_args()
    
    # Determine report type
    if args.weekly:
        report_type = "WEEKLY"
    else:
        # Default to daily if no option specified or --daily is used
        report_type = "DAILY"

    do_sync = args.sync

    report = wrap_up(report_type, do_sync)

    if args.save:
        journal_dir = '/Users/wsq/Codespace/Obsidian/Work/2025/Journals'
        os.makedirs(journal_dir, exist_ok=True)

        # Define the output file path
        now = datetime.now()
        if now.hour < 6:
            report_date = now - timedelta(1)
        else:
            report_date = now
        filename = f"{report_type}_{report_date.strftime('%Y%m%d')}.md"
        filepath = os.path.join(journal_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
    
        print(f"Saved to {filepath}")
