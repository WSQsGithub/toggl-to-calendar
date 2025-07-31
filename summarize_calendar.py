import subprocess
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
import time

import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

@dataclass
class CalendarEvent:
    """日历事件数据类"""
    start: str
    end: str
    summary: str
    calendar: str
    description: str = ""
    is_toggl: bool = False
    full_start: Optional[str] = None
    full_end: Optional[str] = None

@dataclass
class Reminder:
    """提醒事项数据类"""
    due_date: str
    name: str
    list_name: str
    status: str
    priority: str = ""
    body: str = ""

class AppleScriptExecutor:
    """AppleScript执行器"""
    
    @staticmethod
    def execute(script: str) -> str:
        """执行AppleScript并返回结果"""
        try:
            osa_cmd = ['osascript', '-e', script]
            output = subprocess.check_output(osa_cmd, text=True, stderr=subprocess.PIPE)
            
            return output
        except subprocess.CalledProcessError as e:
            print(f"AppleScript 执行失败: {e}")
            if hasattr(e, 'stderr') and e.stderr:
                print(f"错误输出: {e.stderr}")
            return ""

class DataSource(ABC):
    """数据源抽象基类"""
    
    def __init__(self, executor: AppleScriptExecutor):
        self.executor = executor
    
    @abstractmethod
    def get_data(self, start_date: datetime, end_date: datetime) -> List:
        """获取数据的抽象方法"""
        pass
    
    @abstractmethod
    def debug_access(self) -> None:
        """调试访问权限的抽象方法"""
        pass

class CalendarDataSource(DataSource):
    """日历数据源"""
    
    def __init__(self, executor: AppleScriptExecutor, calendar_names: List[str] = None):
        super().__init__(executor)
        self.calendar_names = calendar_names or ["Hobbies", "Work", "Relationships", "Growth", "Personal", "Trash"]
    
    def get_data(self, start_date: datetime, end_date: datetime) -> List[CalendarEvent]:
        """获取日历事件"""
        script = self._build_calendar_script(start_date, end_date)
        output = self.executor.execute(script)
        
        if not output or not output.strip():
            print("日历AppleScript返回空输出")
            return []
        
        return self._parse_calendar_output(output)
    
    def get_data_simple(self, start_date: datetime, end_date: datetime) -> List[CalendarEvent]:
        """获取日历事件（简化版）"""
        script = self._build_simple_calendar_script(start_date, end_date)
        output = self.executor.execute(script)
        
        if not output or not output.strip():
            print("简化日历AppleScript返回空输出")
            return []
        
        return self._parse_simple_calendar_output(output)
    
    def _build_calendar_script(self, start_date: datetime, end_date: datetime) -> str:
        """构建日历AppleScript"""
        calendar_list = '", "'.join(self.calendar_names)
        
        return f'''
        set output to ""
        
        set startDate to (current date)
        set year of startDate to {start_date.year}
        set month of startDate to {start_date.month}
        set day of startDate to {start_date.day}
        set hours of startDate to 0
        set minutes of startDate to 0
        set seconds of startDate to 0

        set endDate to (current date)
        set year of endDate to {end_date.year}
        set month of endDate to {end_date.month}
        set day of endDate to {end_date.day}
        set hours of endDate to 23
        set minutes of endDate to 59
        set seconds of endDate to 59

        set theCalendars to {{"{calendar_list}"}}
        
        tell application "Calendar"
            repeat with calName in theCalendars
                try
                    set theCal to calendar (calName as string)
                    set theEvents to every event of theCal whose start date ≥ startDate and start date ≤ endDate
                    repeat with theEvent in theEvents
                        try
                            set eventSummary to summary of theEvent
                            set eventStartDate to start date of theEvent
                            set eventEndDate to end date of theEvent
                            set isAllDay to allday event of theEvent
                            
                            try
                                set eventDescription to description of theEvent
                            on error
                                set eventDescription to ""
                            end try
                            
                            if isAllDay then
                                set eventStart to "All Day"
                                set eventEnd to "All Day"
                            else
                                try
                                    set eventStart to time string of eventStartDate
                                    set eventEnd to time string of eventEndDate
                                on error
                                    set eventStart to (short date string of eventStartDate) & " " & (time string of eventStartDate)
                                    set eventEnd to (short date string of eventEndDate) & " " & (time string of eventEndDate)
                                end try
                            end if
                            
                            set output to output & eventStart & "|" & eventEnd & "|" & eventSummary & "|" & (calName as string) & "|" & eventDescription & linefeed
                        on error eventErr
                            set output to output & "ERROR processing event in " & (calName as string) & ": " & eventErr & linefeed
                        end try
                    end repeat
                on error calErr
                    set output to output & "ERROR accessing calendar " & (calName as string) & ": " & calErr & linefeed
                end try
            end repeat
        end tell
        
        return output
        '''
    
    def _build_simple_calendar_script(self, start_date: datetime, end_date: datetime) -> str:
        """构建简化日历AppleScript"""
        calendar_list = '", "'.join(self.calendar_names)
        
        return f'''
        set output to ""
        
        set startDate to (current date)
        set year of startDate to {start_date.year}
        set month of startDate to {start_date.month}
        set day of startDate to {start_date.day}
        set hours of startDate to 0
        set minutes of startDate to 0
        set seconds of startDate to 0

        set endDate to (current date)
        set year of endDate to {end_date.year}
        set month of endDate to {end_date.month}
        set day of endDate to {end_date.day}
        set hours of endDate to 23
        set minutes of endDate to 59
        set seconds of endDate to 59

        set theCalendars to {{"{calendar_list}"}}
        
        tell application "Calendar"
            repeat with calName in theCalendars
                try
                    set theCal to calendar (calName as string)
                    set theEvents to every event of theCal whose start date ≥ startDate and start date ≤ endDate
                    repeat with theEvent in theEvents
                        try
                            set eventSummary to summary of theEvent
                            set eventStartDate to start date of theEvent as string
                            set eventEndDate to end date of theEvent as string
                            set isAllDay to allday event of theEvent
                            
                            try
                                set eventDescription to description of theEvent
                            on error
                                set eventDescription to ""
                            end try
                            
                            if isAllDay then
                                set eventTimeInfo to "AllDay"
                            else
                                set eventTimeInfo to "Timed"
                            end if
                            
                            set output to output & eventTimeInfo & "|" & eventStartDate & "|" & eventEndDate & "|" & eventSummary & "|" & (calName as string) & "|" & eventDescription & linefeed
                        on error eventErr
                            set output to output & "ERROR_EVENT|" & (calName as string) & "|" & eventErr & linefeed
                        end try
                    end repeat
                on error calErr
                    set output to output & "ERROR_CAL|" & (calName as string) & "|" & calErr & linefeed
                end try
            end repeat
        end tell
        
        return output
        '''
    
    def _parse_calendar_output(self, output: str) -> List[CalendarEvent]:
        """解析日历输出"""
        events = []
        for line in output.strip().split("\n"):
            if not line.strip() or line.startswith("ERROR"):
                if line.startswith("ERROR"):
                    print("⚠️", line)
                continue
            
            try:
                parts = line.strip().split("|")
                if len(parts) >= 5:
                    start, end, summary, calendar, description = parts[0], parts[1], parts[2], parts[3], parts[4]
                    events.append(CalendarEvent(
                        start=start,
                        end=end,
                        summary=summary,
                        calendar=calendar,
                        description=description,
                        is_toggl="Imported from Toggl - ID" in description
                    ))
            except (ValueError, IndexError) as e:
                print(f"解析日历事件失败: {line}, 错误: {e}")
        
        return events
    
    def _parse_simple_calendar_output(self, output: str) -> List[CalendarEvent]:
        """解析简化日历输出"""
        events = []
        for line in output.strip().split("\n"):
            if not line.strip() or line.startswith("ERROR"):
                if line.startswith("ERROR"):
                    print("⚠️", line)
                continue
            
            try:
                parts = line.strip().split("|")
                if len(parts) >= 6:
                    event_type, start_str, end_str, summary, calendar, description = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]
                    
                    if event_type == "AllDay":
                        start_time = "All Day"
                        end_time = "All Day"
                    else:
                        try:
                            start_time = start_str.split(" ")[-2] if len(start_str.split(" ")) > 2 else "Unknown"
                            end_time = end_str.split(" ")[-2] if len(end_str.split(" ")) > 2 else "Unknown"
                        except:
                            start_time = "Unknown"
                            end_time = "Unknown"
                    
                    events.append(CalendarEvent(
                        start=start_time,
                        end=end_time,
                        summary=summary,
                        calendar=calendar,
                        description=description,
                        is_toggl="Imported from Toggl - ID" in description,
                        full_start=start_str,
                        full_end=end_str
                    ))
            except (ValueError, IndexError) as e:
                print(f"解析简化日历事件失败: {line}, 错误: {e}")
        
        return events
    
    def debug_access(self) -> None:
        """调试日历访问权限"""
        script = '''
        tell application "Calendar"
            set calendarNames to name of every calendar
            set output to "Available calendars: " & linefeed
            repeat with calName in calendarNames
                set output to output & "- " & calName & linefeed
            end repeat
            return output
        end tell
        '''
        
        output = self.executor.execute(script)
        if output:
            print("日历调试信息:")
            print(output)
        else:
            print("无法访问日历应用")

class ReminderDataSource(DataSource):
    """提醒数据源"""
    
    def get_data(self, start_date: datetime, end_date: datetime) -> List[Reminder]:
        """获取提醒事项"""
        reminder_names = ["Work", "Hobbies", "Relationships", "Growth", "Personal"]
        
        # 使用线程池并行执行
        with ThreadPoolExecutor(max_workers=len(reminder_names)) as executor:
            # 提交所有任务
            future_to_name = {
                executor.submit(self._get_reminder_for_list, start_date, end_date, reminder_name): reminder_name
                for reminder_name in reminder_names
            }
            
            all_reminders = []
            
            # 收集结果
            for future in concurrent.futures.as_completed(future_to_name):
                reminder_name = future_to_name[future]
                try:
                    reminders = future.result()
                    all_reminders.extend(reminders)
                    print(f"Successfully processed {reminder_name}: {len(reminders)} reminders")
                except Exception as exc:
                    print(f"Error processing {reminder_name}: {exc}")
        
        return all_reminders
    
    def _get_reminder_for_list(self, start_date: datetime, end_date: datetime, reminder_name: str) -> List[Reminder]:
        """获取单个提醒列表的数据"""
        script = self._build_reminder_script(start_date, end_date, [reminder_name])
        output = self.executor.execute(script)
        # print(f"AppleScript result for {reminder_name}: {output}")
        
        if not output or not output.strip():
            return []
        
        return self._parse_reminder_output(output)
    
    @staticmethod
    def categorize_reminders(reminders: List[Reminder]) -> Dict[str, List[Reminder]]:
        """分类提醒事项 - 只处理过期和完成两种类型"""
        return {
            'overdue': [r for r in reminders if r.status == 'Overdue'],    # 过期未完成
            'completed': [r for r in reminders if r.status == 'Completed'] # 已完成
        }

    def _build_reminder_script(self, start_date: datetime, end_date: datetime, reminder_names: list[str]) -> str:
        """构建优化后的提醒AppleScript，基于原始逻辑只处理过期和完成提醒"""
        reminder_list = '", "'.join(reminder_names)
        
        return f'''
        tell application "Reminders"
            set startDate to (current date)
            set year of startDate to {start_date.year}
            set month of startDate to {start_date.month}
            set day of startDate to {start_date.day}
            set hours of startDate to 0
            set minutes of startDate to 0
            set seconds of startDate to 0

            set endDate to (current date)
            set year of endDate to {end_date.year}
            set month of endDate to {end_date.month}
            set day of endDate to {end_date.day}
            set hours of endDate to 23
            set minutes of endDate to 59
            set seconds of endDate to 59


            set reminderLists to {{"{reminder_list}"}}

            set outputLines to ""
            
            repeat with listName in reminderLists
                set currentList to list listName
                -- Fetch incomplete reminders due on or before endDate
                
                set incomplete_rem to properties of (reminders in currentList whose completed is false and due date is less than or equal to endDate)
                repeat with rem in incomplete_rem
                    tell rem
                        set {{reminderName, reminderDueDate, reminderPriority, reminderBody}} to {{name, due date, priority, body}}
                    end tell
                    set reminderName to reminderName as text
                    set reminderStatus to "Overdue" 
                    
                    set dueDateStr to (date string of reminderDueDate) & " " & (time string of reminderDueDate)

                    if reminderBody is missing value then 
                        set reminderBody to ""
                    else
                        set reminderBody to (reminderBody as text)
                    end if
                    set outputLines to outputLines & "\n" & dueDateStr & "|" & reminderName & "|" & listName & "|" & reminderStatus & "|" & reminderPriority & "|" & reminderBody
                end repeat
                
                set completed_rem to properties of (reminders in currentList whose due date is greater than or equal to startDate and due date is less than or equal to endDate and completed is true)
                repeat with rem in completed_rem

                    tell rem
                        set {{reminderName, reminderDueDate, reminderPriority, reminderBody}} to {{name, due date, priority, body}}
                    end tell

                    set reminderName to reminderName as text
                    set reminderStatus to "Completed" 
                    
                    set dueDateStr to (date string of reminderDueDate) & " " & (time string of reminderDueDate)
                    

                    if reminderBody is missing value then 
                        set reminderBody to ""
                    else
                        set reminderBody to (reminderBody as text)
                    end if
                    
                    set outputLines to outputLines & "\n" & dueDateStr & "|" & reminderName & "|" & listName & "|" & reminderStatus & "|" & reminderPriority & "|" & reminderBody
                end repeat
            end repeat
            
            if outputLines is "" then
                return ""
            else
                return outputLines as text
            end if
        end tell

        '''
    
    def _parse_reminder_output(self, output: str) -> List[Reminder]:
        """解析提醒输出"""
        reminders = []
        for line in output.strip().split("\n"):
            if not line.strip() or line.startswith("ERROR"):
                if line.startswith("ERROR"):
                    print("⚠️", line)
                continue
            
            try:
                parts = line.strip().split("|")
                if len(parts) >= 6:
                    due_date, name, list_name, status, priority, body = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]
                    reminders.append(Reminder(
                        due_date=due_date,
                        name=name,
                        list_name=list_name,
                        status=status,
                        priority=priority,
                        body=body
                    ))
            except (ValueError, IndexError) as e:
                print(f"解析提醒失败: {line}, 错误: {e}")
        
        return reminders
    
    def debug_access(self) -> None:
        """调试提醒访问权限"""
        script = '''
        tell application "Reminders"
            set reminderLists to every list
            set output to "Available reminder lists: " & linefeed
            repeat with reminderList in reminderLists
                set listName to name of reminderList
                set reminderCount to count of (every reminder of reminderList)
                set output to output & "- " & listName & " (" & reminderCount & " reminders)" & linefeed
            end repeat
            return output
        end tell
        '''
        
        output = self.executor.execute(script)
        if output:
            print("提醒调试信息:")
            print(output)
        else:
            print("无法访问提醒应用")


class EventAnalyzer:
    """事件分析器"""
    
    @staticmethod
    def split_events(events: List[CalendarEvent]) -> tuple[List[CalendarEvent], List[CalendarEvent]]:
        """分离计划事件和Toggl事件"""
        planned = [e for e in events if not e.is_toggl]
        actual = [e for e in events if e.is_toggl]
        return planned, actual
    
    @staticmethod
    def categorize_reminders(reminders: List[Reminder]) -> Dict[str, List[Reminder]]:
        """分类提醒事项"""
        return {
            'overdue': [r for r in reminders if r.status == 'Overdue'],
            'completed': [r for r in reminders if r.status == 'Completed'],
        }

class ReportGenerator:
    """报告生成器"""
    
    @staticmethod
    def generate_comprehensive_report(
        start_date_str: str,
        end_date_str: str,
        planned: List[CalendarEvent],
        actual: List[CalendarEvent],
        reminders_dict: Dict[str, List[Reminder]],
        show_descriptions: bool = False
    ) -> str:
        """生成综合报告"""
        date_range = start_date_str if start_date_str == end_date_str else f"{start_date_str} to {end_date_str}"
        lines = [f"🗓️ Comprehensive Daily Summary for {date_range}\n"]
        
        # 日历事件
        lines.append("📅 Planned Calendar Events:")
        if planned:
            for e in planned:
                event_line = f"  {e.start}–{e.end} | {e.summary} | {e.calendar}"
                if show_descriptions and e.description:
                    event_line += f" | Note: {e.description[:50]}..."
                lines.append(event_line)
        else:
            lines.append("  (none)")

        lines.append("\n⏱️ Actual Events (Toggl):")
        if actual:
            for e in actual:
                event_line = f"  {e.start}–{e.end} | {e.summary} | {e.calendar}"
                if show_descriptions and e.description:
                    event_line += f" | Note: {e.description[:50]}..."
                lines.append(event_line)
        else:
            lines.append("  (none)")
        
        # 提醒事项
        lines.append("\n🚨 Overdue Reminders:")
        ReportGenerator._add_reminder_section(lines, reminders_dict['overdue'])
        
        lines.append("\n✅ Completed Reminders:")
        if reminders_dict['completed']:
            for r in reminders_dict['completed']:
                lines.append(f"  ✓ {r.name} | {r.list_name}")
        else:
            lines.append("  (none)")

        # 统计信息
        total_reminders = sum(len(reminders_dict[key]) for key in reminders_dict)
        lines.append(f"\n📊 Summary:")
        lines.append(f"  Calendar Events: {len(planned)} planned, {len(actual)} actual (Toggl)")
        lines.append(f"  Reminders: {total_reminders} total ({len(reminders_dict['overdue'])} overdue, {len(reminders_dict['completed'])} completed)")

        return "\n".join(lines)
    
    @staticmethod
    def _add_reminder_section(lines: List[str], reminders: List[Reminder]) -> None:
        """添加提醒章节"""
        if reminders:
            for r in reminders:
                priority_emoji = {
                    9: "🔴",
                    5: "🟡", 
                    1: "🟢"
                }.get(r.priority, "")
                lines.append(f"  {priority_emoji} {r.name} | {r.list_name} | Due: {r.due_date}")
        else:
            lines.append("  (none)")

class CalendarSummarizer:
    """日历摘要生成器主类"""
    
    def __init__(self, calendar_names: List[str] = None):
        self.executor = AppleScriptExecutor()
        self.calendar_source = CalendarDataSource(self.executor, calendar_names)
        self.reminder_source = ReminderDataSource(self.executor)
        self.analyzer = EventAnalyzer()
        self.report_generator = ReportGenerator()
    
    def generate_summary(self, start_date_str: str, end_date_str: str = None) -> str:
        """生成日程摘要"""
        if end_date_str is None:
            end_date_str = start_date_str
        
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        
        # 获取数据
        t0 = time.perf_counter()
        events = self._get_calendar_events(start_date, end_date)
        print(f"找到 {len(events)} 个日历事件")
        t1 = time.perf_counter()
        print(f"花费 {t1-t0} 秒")
        reminders = self.reminder_source.get_data(start_date, end_date)
        t2 = time.perf_counter()
        print(f"找到 {len(reminders)} 个相关提醒")
        print(f"花费 {t2-t1} 秒")
        # 分析数据
        planned, actual = self.analyzer.split_events(events)
        reminders_dict = self.analyzer.categorize_reminders(reminders)
        
        # 生成报告
        return self.report_generator.generate_comprehensive_report(
            start_date_str, end_date_str, planned, actual, reminders_dict, show_descriptions=True
        )
    
    def _get_calendar_events(self, start_date: datetime, end_date: datetime) -> List[CalendarEvent]:
        """获取日历事件（带回退机制）"""
        # 尝试标准方法
        events = self.calendar_source.get_data(start_date, end_date)
        
        if not events:
            print("尝试简化方法...")
            events = self.calendar_source.get_data_simple(start_date, end_date)
        
        return events
    
    def debug_permissions(self) -> None:
        """调试权限"""
        print("检查日历权限和可用日历...")
        self.calendar_source.debug_access()
        print("\n检查提醒权限和可用列表...")
        self.reminder_source.debug_access()

def main():
    """主函数"""
    # 创建摘要生成器
    summarizer = CalendarSummarizer()
    
    # 调试权限
    # summarizer.debug_permissions()
    print("\n" + "="*50 + "\n")
    
    # 获取昨天的日期
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    # 生成摘要
    print("生成日程摘要...")
    summary = summarizer.generate_summary(yesterday)
    print(summary)

if __name__ == "__main__":
    main()