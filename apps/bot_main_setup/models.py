from django.db import models
from utils.bot import set_webhook_sync, get_info


class Language(models.TextChoices):
    UZBEK = "uz", "Uzbek"
    ENGLISH = "en", "English"
    RUSSIAN = "ru", "Russian"
    SPANISH = "es", "Spanish"
    FRENCH = "fr", "French"
    GERMAN = "de", "German"


class TelegramBot(models.Model):
    name = models.CharField(max_length=30, null=True, blank=True)
    bot_token = models.CharField(max_length=255, unique=True)
    bot_username = models.CharField(max_length=125, blank=True, null=True)
    app_name = models.CharField(max_length=255)
    extra_field = models.JSONField(null=True, blank=True)

    def save(self, *args, **kwargs):
        set_webhook_sync(self.bot_token)
        username, name = get_info(bot_token=self.bot_token)
        self.bot_username = username
        self.name = name

        if not self.app_name.startswith("setup_"):
            self.app_name = f"setup_{self.app_name}"

        super(TelegramBot, self).save(*args, **kwargs)

    def clean(self):
        if not self.app_name.startswith("setup_"):
            self.app_name = f"setup_{self.app_name}"

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Telegram Bot"
        verbose_name_plural = "Telegram Bots"
        unique_together = ("bot_token", "app_name")
        db_table = "telegram_bot"


class TelegramProfile(models.Model):
    bot = models.ManyToManyField(TelegramBot)
    telegram_id = models.PositiveBigIntegerField(unique=True)
    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    language = models.CharField(max_length=255, choices=Language.choices, default=Language.UZBEK, null=True)
    is_bot = models.BooleanField(default=False)
    extra_field = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.username} {self.telegram_id}"

    class Meta:
        verbose_name = "Telegram Profile"
        verbose_name_plural = "Telegram Profiles"
        db_table = "telegram_profile"
