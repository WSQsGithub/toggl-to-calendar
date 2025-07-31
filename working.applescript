tell application "Reminders"
    set startDate to date "07/29/2025 12:00:00 AM"
    set endDate to date "07/31/2025 11:59:59 PM"

    tell startDate
        set its hours to 0
        set its minutes to 0
        set its seconds to 0
    end tell

    tell endDate
        set its hours to 23
        set its minutes to 59
        set its seconds to 59
    end tell


    set reminderLists to {"Work", "Personal", "Growth", "Hobbies", "Relationships"}


    set outputLines to ""
    
    repeat with listName in reminderLists
        set currentList to list listName
        -- Fetch incomplete reminders due on or before endDate
        
        set incomplete_rem to properties of (reminders in currentList whose completed is false and due date is less than or equal to endDate)
        repeat with rem in incomplete_rem
            tell rem
                set {reminderName, reminderDueDate, reminderPriority, reminderBody} to {name, due date, priority, body}
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
                set {reminderName, reminderDueDate, reminderPriority, reminderBody} to {name, due date, priority, body}
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
