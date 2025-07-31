from typing import Optional, Literal
from datetime import datetime, timedelta
from summarize_calendar import CalendarSummarizer
from ai_summary import ReportAnalyzer
from sync import sync 

def wrap_up(option: Optional[Literal["Daily", "Weekly"]] = "Daily") -> None:
    """Generate and analyze calendar reports for Daily or Weekly periods"""
    
    today = datetime.now()
    
    sync()
    
    # Calculate date range based on option
    if option == "Daily":
        start_date = today
        end_date = today
        date_str = today.strftime("%Y-%m-%d")
        report_type = "DAILY"
    elif option == "Weekly":
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
    analyzer = ReportAnalyzer("config.json")

    try:
        # Generate calendar summary based on the option
        if option == "Daily":
            summary = summarizer.generate_summary(start_date.strftime("%Y-%m-%d"))
        else:  # Weekly
            # Assuming CalendarSummarizer can handle date ranges
            summary = summarizer.generate_summary(
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d")
            )
        
        # Analyze the summary with context about the report type
        result = analyzer.generate_analysis(summary, report_type=option)
        
        print("=" * 60)
        print(f"CALENDAR ANALYSIS REPORT - {report_type}")
        print("=" * 60)
        print(f"Period: {date_str}")
        print(f"Generated: {today.strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n" + "=" * 20 + " SUMMARY " + "=" * 20)
        print(summary)
        print("\n" + "=" * 20 + " ANALYSIS " + "=" * 19)
        print(result)
        print("=" * 60)
        
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
    
    return parser.parse_args()

if __name__ == "__main__":
    import argparse
    args = parse_args()
    
    # Determine report type
    if args.weekly:
        report_type = "Weekly"
    else:
        # Default to daily if no option specified or --daily is used
        report_type = "Daily"

    wrap_up(option=report_type)