from library_management.celery import shared_task

@shared_task
def send_book_notification(title):
    print(f"Book issued: {title}")