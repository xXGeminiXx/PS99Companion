#Requires AutoHotkey v2.0
; Bee's Anti-AFK Macro 🐝
; https://www.youtube.com/@BeeBrained-PS99
; https://discord.gg/QVncFccwek
; https://autohotkey.com/ Version 2 required.

; ================== Optional Version Check ==================
; Instead of a numeric comparison, just check if it starts with "2."
if !InStr(A_AhkVersion, "2.")
{
    MsgBox "This script requires AutoHotkey v2.0 or higher."
         . "`nDetected version: " A_AhkVersion
    ExitApp
}

; ================== Configurable Items ==================
INTERACTION_DURATION := 1000   ; How long to press keys in each window (ms)
EXCLUDED_TITLES      := ["Account Manager", "Chrome", "Firefox", "Edge", "Opera", "Brave", "Safari", "Internet Explorer", "Vivaldi"]  ; Window titles to exclude
IDLE_SECONDS         := 300  ; How many seconds to wait between cycles

; ================== GUI Setup ==================
myGUI := Gui("+AlwaysOnTop", "🐝Bee's Anti-AFK Macro 🐝")
mainAction      := myGUI.Add("Text", "x10 y10  w380 h20", "🐝 Press F1 to start, F2 to stop, Esc to exit 🐝")
secondaryAction := myGUI.Add("Text", "x10 y40  w380 h20", "Waiting to start...")
statusText      := myGUI.Add("Text", "x10 y70  w380 h20", "Compatible with Bloxstrap and RAM")
myGUI.Show("x0 y0 w400 h100")

; ================== Global Variables ==================
global running := false   ; Tracks whether the macro is active

; ================== Hotkeys ==================
F1::startMacro()     ; Press F1 to start (or resume)
F2::stopMacro()      ; Press F2 to stop
Esc::ExitApp         ; Press Esc to fully exit the script

; ================== Functions ==================

startMacro() {
    global running

    ; If we're already running, do nothing.
    if running
        return

    running := true
    mainAction.Text      := "🐝 Macro is running 🐝🐝🐝"
    secondaryAction.Text := "Finding Roblox windows..."

    ; Main loop: Continue cycling as long as we're running.
    while running {
        robloxWindows := findRobloxWindows()

        if (robloxWindows.Length = 0) {
            secondaryAction.Text := "No Roblox windows found. Retrying..."
            Sleep 10000
            continue
        }

        secondaryAction.Text := Format("Found {1} Roblox window(s)", robloxWindows.Length)

        ; Interact with each Roblox window
        for hwnd in robloxWindows {
            if !running
                break
            interactWithWindow(hwnd)
        }

        if !running
            break

        ; After we finish each cycle, idle for IDLE_SECONDS while counting down.
        idleCountdown(IDLE_SECONDS)
    }
    stopMacro()
}

stopMacro() {
    global running
    if !running
        return

    running := false
    mainAction.Text      := "🐝 Macro stopped 🐝"
    secondaryAction.Text := "Press F1 to start again"
}

findRobloxWindows() {
    robloxWindows := []
    try {
        winList := WinGetList()  ; Returns an array of HWNDs in v2
    } catch {
        MsgBox "Failed to retrieve the window list."
        ExitApp
    }

    for _, hwnd in winList {
        title := WinGetTitle(hwnd)
        ; Skip any browser windows or other excluded titles
        if isBrowserOrExcluded(title)
            continue
            
        ; Check for various Roblox window names, including Bloxstrap
        if (InStr(title, "Roblox") || InStr(title, "- Roblox") || RegExMatch(title, "Roblox$") || RegExMatch(title, "Roblox \(Place: \d+\)")) {
            robloxWindows.Push(hwnd)
            statusText.Text := "Last detected window: " . title
        }
    }
    
    ; If no standard Roblox windows found, try looking for all windows with "experience" in the title
    ; which may help detect Bloxstrap windows
    if (robloxWindows.Length = 0) {
        for _, hwnd in winList {
            title := WinGetTitle(hwnd)
            ; Skip any browser windows or other excluded titles
            if isBrowserOrExcluded(title)
                continue
                
            if (InStr(title, "experience") || InStr(title, "Experience")) {
                robloxWindows.Push(hwnd)
                statusText.Text := "Last detected window: " . title
            }
        }
    }
    
    return robloxWindows
}

isBrowserOrExcluded(title) {
    global EXCLUDED_TITLES
    
    ; Check specifically excluded titles
    for excluded in EXCLUDED_TITLES {
        if InStr(title, excluded) {
            return true
        }
    }
    
    ; Additional browser detection logic
    if (RegExMatch(title, " - Chrome$") || 
        RegExMatch(title, " - Edge$") ||
        RegExMatch(title, " - Firefox$") ||
        RegExMatch(title, " - Opera$") ||
        RegExMatch(title, " - Brave$") ||
        RegExMatch(title, " - Safari$") ||
        InStr(title, "Firefox") ||
        InStr(title, "Chrome") ||
        InStr(title, "Opera") ||
        InStr(title, "Brave") ||
        InStr(title, "Safari") ||
        InStr(title, "Edge")) {
        return true
    }
    
    return false
}

interactWithWindow(hwnd) {
    global INTERACTION_DURATION, running

    WinActivate(hwnd)
    WinWaitActive(hwnd, 2) ; Wait up to 2s for the window to be active
    secondaryAction.Text := Format("Interacting with window: {1}", WinGetTitle(hwnd))

    startTime := A_TickCount
    while (A_TickCount - startTime < INTERACTION_DURATION && running) {
        spamKeys()
    }
}

spamKeys() {
    if !running
        return
    ; Press and hold Spacebar
    SendInput("{Space down}")
    Sleep 500  ; Adjust this duration as needed (currently holding Spacebar for 1 second)
    ; Release Spacebar
    SendInput("{Space up}")
    Sleep 500   ; Adjust this delay before pressing other keys
    SendInput("{r}")
    Sleep 500
}

idleCountdown(seconds) {
    global running

    count := seconds
    while (count > 0 && running) {
        secondaryAction.Text := Format("Idling for {1} second(s) until next cycle", count)
        Sleep 1000
        count--
    }
    ; When done, either we finished idling or user pressed F2/Esc.
    if running
        secondaryAction.Text := "Finding Roblox windows..."
}
