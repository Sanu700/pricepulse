from .console_service import ConsoleNotificationService


class NotificationService:
    @staticmethod
    def notify(notification: dict):
        ConsoleNotificationService.send(notification)