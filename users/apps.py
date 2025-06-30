from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        try:
            # ✅ מייבאים ישירות מתוך cron
            from sarms_backend.cron import check_due_dates_and_notify
            import threading

            def run_scheduler():
                while True:
                    print("🔄 בודק בקשות עם תאריך יעד...")
                    check_due_dates_and_notify()
                    import time
                    time.sleep(86400)  # כל 24 שעות

            thread = threading.Thread(target=run_scheduler, daemon=True)
            thread.start()
            print("✅ תזמון אוטומטי הופעל")

        except Exception as e:
            print(f"❌ שגיאה בהפעלת scheduler או התראות: {e}")
