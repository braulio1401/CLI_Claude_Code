import time
from collections.abc import Iterable

import pyautogui
import pywhatkit


def _format_phone_number(phone: str) -> str:
    normalized = phone.strip().replace(" ", "").replace("-", "")
    if not normalized.startswith("+"):
        normalized = f"+{normalized}"
    return normalized


def _focus_whatsapp_window() -> None:
    try:
        windows = pyautogui.getWindowsWithTitle("WhatsApp")
        if windows:
            window = windows[0]
            if not window.isActive:
                window.activate()
            if not window.isMaximized:
                window.maximize()
    except Exception:
        pass


def _click_bottom_input() -> None:
    width, height = pyautogui.size()
    pyautogui.click(width // 2, int(height * 0.92))


def send_whatsapp_notifications(recipients: Iterable[str], message: str) -> list[str]:
    errors: list[str] = []
    for raw_phone in recipients:
        try:
            phone = _format_phone_number(raw_phone)
            pywhatkit.sendwhatmsg_instantly(
                phone,
                message,
                wait_time=30,
                tab_close=False,
                close_time=10,
            )
            time.sleep(6)
            _focus_whatsapp_window()
            time.sleep(1)
            try:
                _click_bottom_input()
                time.sleep(1)
                pyautogui.press("enter")
            except Exception:
                pyautogui.press("enter")
        except Exception as exc:
            errors.append(f"WhatsApp {raw_phone}: {exc}")
    return errors
