#Requires AutoHotkey v2.0
; 🐝 Simple Click and F Macro with GUI 🐝
; This script is designed to automate two actions in a game:
; 1. Click the item in your inventory (at your mouse pointer) to summon it.
; 2. Press the "F" key, which is used to handle errors or interact with the inventory.
; The macro alternates between clicking and pressing "F" every 1 second, ensuring smooth operation.

; ================== Configurable Timing ==================
CLICK_DELAY := 1000  ; Delay after clicking in milliseconds
F_DELAY := 1000      ; Delay after pressing F in milliseconds

; ================== Global Variables ==================
global running := false  ; Tracks whether the macro is active
myGUI := ""              ; GUI object

; ================== GUI Setup ==================
setupGUI()

; ================== Hotkeys ==================
F1::startMacro()  ; Press F1 to start (or resume)
F2::stopMacro()   ; Press F2 to stop
Esc::ExitApp      ; Press Esc to exit the script

; ================== Functions ==================

; Sets up the GUI window to display macro status
setupGUI() {
    global myGUI
    myGUI := Gui("+AlwaysOnTop", "🐝 Simple Click and F Macro 🐝")
    myGUI.Add("Text", "x10 y10 w380 h20", "🐝 Press F1 to start, F2 to stop, Esc to exit 🐝")
    myGUI.Add("Text", "x10 y40 w380 h20", "Waiting to start...").Name := "Status"
    myGUI.Show("x0 y0 w400 h100")
}

; Updates the GUI status text
updateStatus(text) {
    global myGUI
    myGUI["Status"].Text := text
}

; Starts the macro loop
startMacro() {
    global running, CLICK_DELAY, F_DELAY

    ; Prevent starting the macro multiple times
    if running
        return

    running := true
    updateStatus("🐝 Macro is running 🐝")

    ; Main loop for clicking and pressing F alternately
    while running {
        SendInput("{Click}")  ; Click where the mouse is hovering
        Sleep CLICK_DELAY     ; Wait after clicking

        SendInput("{F}")      ; Press the "F" key
        Sleep F_DELAY         ; Wait after pressing F
    }
}

; Stops the macro loop
stopMacro() {
    global running
    running := false
    updateStatus("Macro stopped. Press F1 to start again.")
}
