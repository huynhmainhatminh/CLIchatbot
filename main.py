import asyncio
import json
import aiohttp
from prompt_toolkit import PromptSession, Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.application.current import get_app
from prompt_toolkit.layout.containers import Float, HSplit, VSplit, Window, FloatContainer
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.widgets import (
    Button,
    Dialog,
    Frame,
    Label,
    TextArea,
)

bindings = KeyBindings()
session = PromptSession()

floats = []


chat_display = TextArea(
        read_only=False,
        scrollbar=True,
        wrap_lines=True,
        style="bg:#444444 fg:white"
)

input_box = TextArea(
        height=7,
        multiline=True,
        prompt="> ",
        style="bg:#444444 fg:white"
)


async def show_about_dialog():
    about_dialog = Dialog(
        title="About",
        body=Label(text="This is the chatbotCLI application.\nCreated by Huỳnh Mai Nhật Minh."),
        buttons=[
            Button(text="OK", handler=lambda: asyncio.create_task(close_dialog()))
        ],
        width=40,
        modal=True
    )
    floats.append(Float(content=about_dialog))
    app.invalidate()


async def close_dialog():
    floats.pop()
    app.invalidate()


async def typewriter_effect(text_widget, message, delay=0.1):
    for char in message:
        text_widget.text += char
        text_widget.buffer.cursor_position = len(text_widget.text)
        await asyncio.sleep(delay)  # Non-blocking delay


async def clear_text_input():
    input_box.text = ""


async def exit_bt():
    get_app().exit(result=True)


async def send_message():

    send_button.handler = lambda: None  # Tạm thời vô hiệu hóa handler
    send_button.text = "WAIT"
    send_button.window.style = "bg:#cccccc fg:#666666 bold"  # Màu xám khi vô hiệu hóa

    message = input_box.text.strip()
    if message:
        chat_display.text += f"\nYou: {message}\n"
        input_box.text = ""  # Xóa nội dung của input_box
        chat_display.buffer.cursor_position = len(chat_display.text)  # Đảm bảo cuộn đến cuối
        async with aiohttp.ClientSession(headers={
            'authority': 'chatbox.computer.com',
            'accept': '*/*',
            'content-type': 'application/json; charset=utf-8',
        }) as session:
            json_data = {'question': message}
            response = await session.post(
                'https://chatbox.computer.com/api/questions/617143/stream/',
                json=json_data,
            )
            response_text = await response.text()
            response_lines = response_text.strip().split("\n")
            filtered_data = [json.loads(item) for item in response_lines if item.strip()]
            sentence = ''.join(item['answer'] for item in filtered_data)
            await typewriter_effect(chat_display, f"\nBot: {sentence}\n", delay=0.03)
            chat_display.buffer.cursor_position = len(chat_display.text)  # Đảm bảo cuộn đến cuối

            # Kích hoạt lại nút
    send_button.text = "SEND"
    send_button.window.style = "bg:#9e9e9e fg:#FFFFFF bold"
    send_button.handler = lambda: asyncio.create_task(send_message())  # Kích hoạt lại handler
    app.invalidate()


send_button = Button(
        text="SEND",  # Unicode arrow icon
        handler=lambda: asyncio.create_task(send_message())
)
send_button.window.style = "bg:#9e9e9e fg:#FFFFFF bold"


clear_text_button = Button(
        text="CLEAR",  # Unicode arrow icon
        handler=lambda: asyncio.create_task(clear_text_input()),
)
clear_text_button.window.style = "bg:#9e9e9e fg:#FFFFFF bold"

exit_button = Button(
        text="EXIT",  # Unicode arrow icon
        handler=lambda: asyncio.create_task(exit_bt()),
)
exit_button.window.style = "bg:#9e9e9e fg:#FFFFFF bold"


# Tạo các button
new_chat_button = Button(text="New Chat", handler=lambda: asyncio.create_task(clear_text_input()), width=12)
undo_button = Button(text="Clear Data", handler=lambda: asyncio.create_task(clear_text_input()), width=14)
redo_button = Button(text="Search", handler=lambda: asyncio.create_task(clear_text_input()), width=10)
about_button = Button(text="About", handler=lambda: asyncio.create_task(show_about_dialog()), width=9)

left_screen = HSplit([
    VSplit([
        Frame(body=new_chat_button),
        Frame(body=undo_button),
        Frame(body=redo_button),
        Frame(body=about_button),
    ]),
    Window(
        content=FormattedTextControl("Left Screen Content"),
        style="bg:#444444 fg:white",
        width=30,
    )
])

layout = FloatContainer(
    content=VSplit(
        [
            VSplit(
            [
                Frame(body=left_screen, style="bg:#6c6c6c"),
            ]
        ),
        HSplit(
            [
                Frame(body=chat_display, style="bg:#6c6c6c"),
                VSplit([
                    Frame(body=input_box, style="bg:#6c6c6c"),  # Input box
                    HSplit([
                        Frame(body=send_button, style="bg:#6c6c6c"),  # Send button
                        Frame(body=clear_text_button, style="bg:#6c6c6c"),  # clear button
                        Frame(body=exit_button, style="bg:#6c6c6c"),  # exit button
                    ])
                ])
            ]
        ),
        ]
    ),
    floats=floats
)


app = Application(
    layout=Layout(layout, focused_element=input_box), key_bindings=bindings, full_screen=True,
    mouse_support=True
    )


@bindings.add("c-c")
async def _(event):
    event.app.exit()


async def main():
    chat_display.text += "Bot: Chào bạn, bạn cần giúp đỡ gì?\n"

    await app.run_async()


if __name__ == '__main__':
    asyncio.run(main())
