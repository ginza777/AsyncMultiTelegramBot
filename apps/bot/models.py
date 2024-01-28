from django.db import models
from utils.bot import set_webhook_sync, get_info


class Language(models.TextChoices):
    UZBEK = "uz", "Uzbek"


class TelegramBot(models.Model):
    name = models.CharField(max_length=30, null=True, blank=True)
    bot_token = models.CharField(max_length=255)
    bot_username = models.CharField(max_length=125, blank=True, null=True)
    app_name= models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        set_webhook_sync(self.bot_token)
        username, name = get_info(bot_token=self.bot_token)
        self.bot_username = username
        self.name = name

        if not self.app_name.startswith("setup_"):
            self.app_name = f"setup_{self.app_name}"

        super(TelegramBot, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class TelegramProfile(models.Model):
    bot = models.ForeignKey(TelegramBot, models.CASCADE, null=True)
    telegram_id = models.PositiveBigIntegerField()
    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    language = models.CharField(max_length=255, choices=Language.choices, default=Language.UZBEK, null=True)
    is_bot = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.username} {self.telegram_id}"
