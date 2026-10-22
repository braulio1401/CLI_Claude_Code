import pywhatkit

from students_notifications import whatsapp_sender


def test_format_phone_number() -> None:
    assert whatsapp_sender._format_phone_number("521234567890") == "+521234567890"
    assert whatsapp_sender._format_phone_number("+521234567890") == "+521234567890"


def test_send_whatsapp_notifications_calls_pywhatkit(monkeypatch) -> None:
    calls: list[tuple[str, str, int, bool, int]] = []

    def fake_sendwhatmsg_instantly(phone_no: str, message: str, wait_time: int = 15, tab_close: bool = False, close_time: int = 3) -> None:
        calls.append((phone_no, message, wait_time, tab_close, close_time))

    monkeypatch.setattr(pywhatkit, "sendwhatmsg_instantly", fake_sendwhatmsg_instantly)
    monkeypatch.setattr(whatsapp_sender.time, "sleep", lambda _: None)
    monkeypatch.setattr(whatsapp_sender.pyautogui, "getWindowsWithTitle", lambda title: [type("W", (), {"isActive": False, "isMaximized": False, "activate": lambda self: None, "maximize": lambda self: None})()])
    monkeypatch.setattr(whatsapp_sender.pyautogui, "size", lambda: (1920, 1080))
    monkeypatch.setattr(whatsapp_sender.pyautogui, "click", lambda x, y: None)
    monkeypatch.setattr(whatsapp_sender.pyautogui, "press", lambda _: None)

    errors = whatsapp_sender.send_whatsapp_notifications(["521234567890"], "Hola prueba")
    assert errors == []
    assert len(calls) == 1
    assert calls[0][0] == "+521234567890"
    assert calls[0][1] == "Hola prueba"
    assert calls[0][2] == 30
    assert calls[0][3] is False
    assert calls[0][4] == 10
